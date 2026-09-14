"""Offline unit tests for backend/rag/embedder.py — Embedder wrapper.

All tests are synthetic/offline — no network, no model download.
SentenceTransformer is mocked so tests are deterministic and CI-safe.
"""

import sys
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Lightweight SentenceTransformer mock
# ---------------------------------------------------------------------------

FAKE_DIM = 384
FAKE_EMB = np.ones(FAKE_DIM, dtype="float32") * 0.1


class _FakeModel:
    """Fake SentenceTransformer — deterministic embeddings."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._dim = FAKE_DIM
        self.encode_calls: list[dict] = []

    def encode(self, texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True):
        # Record call for assertions
        self.encode_calls.append(
            {
                "texts": texts,
                "batch_size": batch_size,
                "show_progress_bar": show_progress_bar,
                "convert_to_numpy": convert_to_numpy,
            }
        )
        if isinstance(texts, str):
            # single text -> single vector
            vec = np.ones(self._dim, dtype="float32") * 0.42
            return vec
        # list of texts -> matrix
        n = len(texts)
        mat = np.zeros((n, self._dim), dtype="float32")
        for i in range(n):
            mat[i] = np.ones(self._dim, dtype="float32") * (0.1 + i * 0.01)
        return mat

    def get_sentence_embedding_dimension(self):
        return self._dim


_fake_st_module = MagicMock()
_fake_st_module.SentenceTransformer = _FakeModel
sys.modules["sentence_transformers"] = _fake_st_module

# Load embedder directly without triggering rag/__init__.py heavy deps
_EMB_PATH = Path(__file__).resolve().parents[1] / "backend" / "rag" / "embedder.py"
_spec = importlib.util.spec_from_file_location("rag.embedder", _EMB_PATH)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["rag.embedder"] = _mod
_spec.loader.exec_module(_mod)

Embedder = _mod.Embedder
get_embedder = _mod.get_embedder


# ---------------------------------------------------------------------------
# Helpers — reset singleton between tests
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_singleton():
    _mod._embedder_instance = None
    yield
    _mod._embedder_instance = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInit:
    def test_default_model_name(self):
        e = Embedder()
        assert e.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert e.model is not None
        assert isinstance(e.model, _FakeModel)

    def test_custom_model_name(self):
        e = Embedder(model_name="custom/model")
        assert e.model_name == "custom/model"
        assert e.model.model_name == "custom/model"

    def test_model_has_dimension(self):
        e = Embedder()
        assert e.get_embedding_dimension() == FAKE_DIM

    def test_model_load_called(self):
        e = Embedder(model_name="test/model")
        assert e.model is not None
        assert e.model._dim == FAKE_DIM

    def test_load_model_failure_raises(self):
        # Must patch where Embedder looks it up — the module namespace, not the mock source
        with patch.object(_mod, "SentenceTransformer", side_effect=RuntimeError("load failed")):
            with pytest.raises(RuntimeError, match="load failed"):
                Embedder(model_name="bad/model")


class TestEmbedChunks:
    def test_empty_returns_empty(self):
        e = Embedder()
        assert e.embed_chunks([]) == []

    def test_single_chunk_adds_embedding(self):
        e = Embedder()
        chunks = [{"text": "hello world", "metadata": {"i": 0}}]
        result = e.embed_chunks(chunks)
        assert len(result) == 1
        assert "embedding" in result[0]
        assert isinstance(result[0]["embedding"], np.ndarray)
        assert result[0]["embedding"].shape == (FAKE_DIM,)
        # original chunk mutated — same object returned
        assert result is chunks

    def test_multiple_chunks_batch(self):
        e = Embedder()
        chunks = [{"text": f"chunk {i}", "metadata": {}} for i in range(5)]
        result = e.embed_chunks(chunks)
        assert len(result) == 5
        for c in result:
            assert "embedding" in c
            assert c["embedding"].shape == (FAKE_DIM,)
        # embeddings should be distinct (mock varies by index)
        assert not np.allclose(result[0]["embedding"], result[1]["embedding"])

    def test_embed_chunks_uses_batch_params(self):
        e = Embedder()
        chunks = [{"text": "a", "metadata": {}}]
        e.embed_chunks(chunks)
        call = e.model.encode_calls[-1]
        assert call["batch_size"] == 32
        assert call["show_progress_bar"] is True
        assert call["convert_to_numpy"] is True

    def test_embed_chunks_preserves_text_and_metadata(self):
        e = Embedder()
        chunks = [{"text": "keep me", "metadata": {"chunk_index": 7, "extra": "x"}}]
        result = e.embed_chunks(chunks)
        assert result[0]["text"] == "keep me"
        assert result[0]["metadata"]["chunk_index"] == 7
        assert result[0]["metadata"]["extra"] == "x"

    def test_embed_chunks_embedding_values(self):
        e = Embedder()
        chunks = [{"text": "t", "metadata": {}} for _ in range(3)]
        result = e.embed_chunks(chunks)
        # mock: row i = 0.1 + i*0.01
        assert result[0]["embedding"][0] == pytest.approx(0.1, abs=1e-6)
        assert result[1]["embedding"][0] == pytest.approx(0.11, abs=1e-6)
        assert result[2]["embedding"][0] == pytest.approx(0.12, abs=1e-6)


class TestEmbedText:
    def test_embed_single_text(self):
        e = Embedder()
        vec = e.embed_text("single query")
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (FAKE_DIM,)
        assert vec[0] == pytest.approx(0.42, abs=1e-6)

    def test_embed_text_calls_encode_with_string(self):
        e = Embedder()
        e.embed_text("hello")
        call = e.model.encode_calls[-1]
        assert call["texts"] == "hello"
        assert call["convert_to_numpy"] is True

    def test_embed_text_different_inputs(self):
        e = Embedder()
        v1 = e.embed_text("query one")
        v2 = e.embed_text("query two")
        # mock returns constant for single text, so equal — verifies determinism
        assert np.allclose(v1, v2)


class TestGetEmbeddingDimension:
    def test_dimension_matches_model(self):
        e = Embedder()
        assert e.get_embedding_dimension() == FAKE_DIM
        assert e.get_embedding_dimension() == e.model.get_sentence_embedding_dimension()


class TestGetEmbedderSingleton:
    def test_singleton_same_instance(self):
        a = get_embedder()
        b = get_embedder()
        assert a is b

    def test_singleton_reuses_model(self):
        a = get_embedder(model_name="first/model")
        assert a.model_name == "first/model"
        b = get_embedder(model_name="second/model")
        # second call returns same instance — model_name unchanged
        assert b is a
        assert b.model_name == "first/model"

    def test_singleton_after_reset_creates_new(self):
        a = get_embedder()
        _mod._embedder_instance = None
        b = get_embedder(model_name="new/model")
        assert b is not a
        assert b.model_name == "new/model"

    def test_singleton_default_model(self):
        inst = get_embedder()
        assert inst.model_name == "sentence-transformers/all-MiniLM-L6-v2"
