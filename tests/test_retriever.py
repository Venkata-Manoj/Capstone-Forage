"""Offline unit tests for backend/rag/retriever.py — Retriever RAG logic.

All tests are synthetic/offline — no real embeddings, no FAISS, no network.
Embedder and VectorStore are mocked; retriever loaded directly to avoid
rag/__init__.py heavy deps (sentence_transformers).
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Load retriever directly without triggering rag/__init__.py
# ---------------------------------------------------------------------------
# Mock the embedder/vector_store modules so retriever import succeeds without
# sentence_transformers/faiss.
sys.modules.setdefault("sentence_transformers", MagicMock())

# Create lightweight mock for backend.rag.embedder.get_embedder
# We patch it after load — retriever imports `from .embedder import get_embedder`
# So we need to provide a fake package path.
# Easiest: load file directly and patch sys.modules for its dependencies.

# Provide dummy faiss for vector_store import (not needed for retriever but
# vector_store module is imported via `from .vector_store import VectorStore`)
sys.modules.setdefault("faiss", MagicMock())

# Load retriever via importlib without going through package __init__
_RETR_PATH = Path(__file__).resolve().parents[1] / "backend" / "rag" / "retriever.py"
_spec = importlib.util.spec_from_file_location("rag.retriever", _RETR_PATH)
_mod = importlib.util.module_from_spec(_spec)
# Mock relative imports: retriever does `from .embedder import get_embedder`
# and `from .vector_store import VectorStore` — provide them in sys.modules
# before exec
import types

_fake_embedder_mod = types.ModuleType("rag.embedder")
_fake_embedder_mod.get_embedder = MagicMock(return_value=MagicMock(embed_text=lambda q: np.ones(4)))
sys.modules["rag.embedder"] = _fake_embedder_mod

_fake_vs_mod = types.ModuleType("rag.vector_store")
_fake_vs_mod.VectorStore = MagicMock
sys.modules["rag.vector_store"] = _fake_vs_mod

# Also need parent package
sys.modules.setdefault("rag", types.ModuleType("rag"))

sys.modules["rag.retriever"] = _mod
_spec.loader.exec_module(_mod)
Retriever = _mod.Retriever


# ---------------------------------------------------------------------------
# Helpers — fake embedder / vector store
# ---------------------------------------------------------------------------


class FakeEmbedder:
    def __init__(self, dim=4):
        self.dim = dim
        self.calls = []

    def embed_text(self, text: str):
        self.calls.append(text)
        # deterministic embedding: hash-ish
        h = abs(hash(text)) % 1000
        rng = np.random.default_rng(h)
        return rng.random(self.dim, dtype=np.float32)


class FakeVectorStore:
    def __init__(self, chunks_with_dist=None):
        # chunks_with_dist: list of (chunk, distance)
        self._data = chunks_with_dist or []
        self.last_query = None
        self.last_top_k = None

    def search(self, query_embedding, top_k):
        self.last_query = query_embedding
        self.last_top_k = top_k
        # Return up to top_k
        return self._data[:top_k]


def _make_chunk(text="hello world", section_title=None, meta_extra=None):
    chunk = {"text": text, "metadata": {}}
    if section_title:
        chunk["metadata"]["section_title"] = section_title
    if meta_extra:
        chunk["metadata"].update(meta_extra)
    return chunk


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRetrieverInit:
    def test_init_with_embedder(self):
        vs = FakeVectorStore()
        emb = FakeEmbedder()
        r = Retriever(vector_store=vs, embedder=emb)
        assert r.vector_store is vs
        assert r.embedder is emb

    def test_init_without_embedder_uses_global(self):
        # When embedder=None, Retriever calls get_embedder()
        vs = FakeVectorStore()
        fake_global = FakeEmbedder()
        _fake_embedder_mod.get_embedder.return_value = fake_global
        r = Retriever(vector_store=vs, embedder=None)
        assert r.embedder is fake_global
        # restore
        _fake_embedder_mod.get_embedder.return_value = MagicMock(embed_text=lambda q: np.ones(4))


class TestDistanceToSimilarity:
    def test_zero_distance_is_one(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        assert r._distance_to_similarity(0.0) == 1.0

    def test_large_distance_near_zero(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        assert r._distance_to_similarity(1e6) < 0.001
        assert r._distance_to_similarity(1e6) > 0

    def test_monotonic_decreasing(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        sim0 = r._distance_to_similarity(0)
        sim1 = r._distance_to_similarity(1)
        sim5 = r._distance_to_similarity(5)
        assert sim0 > sim1 > sim5

    def test_formula(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        for d in [0, 0.5, 1, 2, 10]:
            assert r._distance_to_similarity(d) == pytest.approx(1.0 / (1.0 + d))


class TestRetrieve:
    def test_retrieve_basic(self):
        chunks = [(_make_chunk("a"), 0.5), (_make_chunk("b"), 1.0)]
        vs = FakeVectorStore(chunks)
        emb = FakeEmbedder()
        r = Retriever(vs, emb)
        out = r.retrieve("hello", top_k=5)
        assert len(out) == 2
        assert out[0]["text"] == "a"
        assert out[0]["similarity_score"] == pytest.approx(1.0 / 1.5)
        assert out[0]["distance"] == 0.5
        assert "similarity_score" in out[1]
        # embed called
        assert emb.calls == ["hello"]

    def test_retrieve_top_k_respected(self):
        chunks = [(_make_chunk(str(i)), float(i)) for i in range(10)]
        vs = FakeVectorStore(chunks)
        r = Retriever(vs, FakeEmbedder())
        out = r.retrieve("q", top_k=3)
        assert len(out) == 3
        assert vs.last_top_k == 3

    def test_retrieve_empty_store(self):
        vs = FakeVectorStore([])
        r = Retriever(vs, FakeEmbedder())
        out = r.retrieve("q", top_k=5)
        assert out == []

    def test_retrieve_min_similarity_filters(self):
        # distance 0 -> sim 1.0, distance 1 -> sim 0.5, distance 9 -> sim 0.1
        chunks = [(_make_chunk("close"), 0.1), (_make_chunk("mid"), 1.0), (_make_chunk("far"), 9.0)]
        vs = FakeVectorStore(chunks)
        r = Retriever(vs, FakeEmbedder())
        out = r.retrieve("q", top_k=5, min_similarity=0.4)
        # 0.1 -> 0.909 keep, 1.0 -> 0.5 keep, 9.0 -> 0.1 filtered
        assert len(out) == 2
        texts = [c["text"] for c in out]
        assert "far" not in texts

    def test_retrieve_min_similarity_none_no_filter(self):
        chunks = [(_make_chunk("x"), 100)]
        vs = FakeVectorStore(chunks)
        r = Retriever(vs, FakeEmbedder())
        out = r.retrieve("q", min_similarity=None)
        assert len(out) == 1

    def test_retrieve_original_chunk_not_mutated(self):
        chunk = _make_chunk("orig")
        vs = FakeVectorStore([(chunk, 0.5)])
        r = Retriever(vs, FakeEmbedder())
        out = r.retrieve("q")
        # original chunk should not have similarity_score
        assert "similarity_score" not in chunk
        assert "distance" not in chunk
        assert "similarity_score" in out[0]


class TestRetrieveForSection:
    def test_retrieve_for_section_known_keywords(self):
        vs = FakeVectorStore([(_make_chunk("x"), 0.2)])
        emb = FakeEmbedder()
        r = Retriever(vs, emb)
        out = r.retrieve_for_section("Methodology", "My Project", top_k=5)
        assert len(out) == 1
        # query should contain project + section + keywords
        assert emb.calls[0].startswith("My Project - Methodology")
        assert "approach" in emb.calls[0]
        assert vs.last_top_k == 5

    def test_retrieve_for_section_unknown_keywords(self):
        vs = FakeVectorStore([(_make_chunk("y"), 0.3)])
        emb = FakeEmbedder()
        r = Retriever(vs, emb)
        r.retrieve_for_section("CustomSection", "Proj", top_k=2)
        # no extra keywords appended, just title-section
        assert emb.calls[0] == "Proj - CustomSection"

    def test_retrieve_for_section_top_k_forwarded(self):
        vs = FakeVectorStore([(_make_chunk(str(i)), 0.1 * i) for i in range(5)])
        emb = FakeEmbedder()
        r = Retriever(vs, emb)
        r.retrieve_for_section("Introduction", "T", top_k=1)
        assert vs.last_top_k == 1


class TestGetContextWindow:
    def test_empty_chunks(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        assert r.get_context_window([], max_tokens=100) == ""

    def test_single_chunk(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        ctx = r.get_context_window([_make_chunk("hello")], max_tokens=1000)
        assert ctx == "hello"

    def test_section_title_header_prepended(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        chunk = _make_chunk("content here", section_title="Results")
        ctx = r.get_context_window([chunk], max_tokens=1000)
        assert "## Results" in ctx
        assert "content here" in ctx

    def test_max_tokens_truncation(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        chunks = [_make_chunk("A" * 100) for _ in range(10)]
        # max_tokens=10 => 40 chars, each chunk 100 chars -> only 0 or first? test truncation
        ctx = r.get_context_window(chunks, max_tokens=10)
        # Should include at most 0 or truncated; must be shorter than full join
        full = "\n\n".join(["A" * 100] * 10)
        assert len(ctx) < len(full)
        # With small budget, at most one chunk or zero
        assert ctx.count("A" * 100) <= 1

    def test_multiple_chunks_joined(self):
        vs = FakeVectorStore()
        r = Retriever(vs, FakeEmbedder())
        chunks = [_make_chunk(f"part {i}") for i in range(3)]
        ctx = r.get_context_window(chunks, max_tokens=1000)
        assert "part 0" in ctx
        assert "part 2" in ctx
        assert ctx.count("\n\n") == 2
