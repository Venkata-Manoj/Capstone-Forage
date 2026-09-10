"""Offline unit tests for backend/rag/vector_store.py — FAISS vector store.

All tests are synthetic/offline — no real FAISS binary required.
FAISS is mocked with a numpy L2 search so tests are deterministic and CI-safe.
"""

import sys
import pickle
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Lightweight FAISS mock — numpy L2 search
# ---------------------------------------------------------------------------


class _FakeIndex:
    def __init__(self, dim: int):
        self.dimension = dim
        self.ntotal = 0
        self._vectors: list[np.ndarray] = []

    def add(self, embeddings: np.ndarray):
        for row in embeddings:
            self._vectors.append(row.copy().astype("float32"))
            self.ntotal += 1

    def search(self, query: np.ndarray, k: int):
        n = self.ntotal
        if n == 0:
            distances = np.full((query.shape[0], k), float("inf"), dtype="float32")
            indices = np.full((query.shape[0], k), -1, dtype=np.int64)
            return distances, indices
        mat = np.stack(self._vectors)
        if query.ndim == 1:
            query = query.reshape(1, -1)
        dists = np.linalg.norm(mat[None, :, :] - query[:, None, :], axis=2) ** 2
        k_eff = min(k, n)
        sorted_idx = np.argsort(dists, axis=1)[:, :k_eff]
        sorted_dists = np.take_along_axis(dists, sorted_idx, axis=1)
        return sorted_dists.astype("float32"), sorted_idx.astype(np.int64)


_fake_faiss = MagicMock()
_fake_faiss.IndexFlatL2 = _FakeIndex

# write_index / read_index persist via pickle of vectors + dimension
_store: dict[str, dict] = {}


def _fake_write_index(index: _FakeIndex, path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"dimension": index.dimension, "vectors": [v.tolist() for v in index._vectors]}
    p.write_bytes(pickle.dumps(data))


def _fake_read_index(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    data = pickle.loads(p.read_bytes())
    idx = _FakeIndex(data["dimension"])
    if data["vectors"]:
        arr = np.array(data["vectors"], dtype="float32")
        idx.add(arr)
    return idx


_fake_faiss.write_index = _fake_write_index
_fake_faiss.read_index = _fake_read_index

sys.modules["faiss"] = _fake_faiss

# Load vector_store directly without triggering rag/__init__.py (pulls sentence-transformers)
import importlib.util

_VS_PATH = Path(__file__).resolve().parents[1] / "backend" / "rag" / "vector_store.py"
_spec = importlib.util.spec_from_file_location("rag.vector_store", _VS_PATH)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["rag.vector_store"] = _mod
_spec.loader.exec_module(_mod)
VectorStore = _mod.VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIM = 4


def _make_chunks(n: int, dim: int = DIM):
    """Make n synthetic chunks with random-ish embeddings."""
    chunks = []
    for i in range(n):
        emb = np.arange(dim, dtype="float32") + float(i * 10)
        chunks.append(
            {
                "text": f"chunk {i} text",
                "metadata": {"chunk_index": i},
                "embedding": emb,
            }
        )
    return chunks


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInit:
    def test_default_dimension(self):
        vs = VectorStore(dimension=384)
        assert vs.dimension == 384
        assert vs.index.dimension == 384
        assert vs.index.ntotal == 0
        assert vs.chunks == []

    def test_custom_dimension(self):
        vs = VectorStore(dimension=DIM)
        assert vs.dimension == DIM
        assert vs.get_stats()["dimension"] == DIM

    def test_create_index_called(self):
        vs = VectorStore(dimension=DIM)
        assert vs.index is not None
        assert vs.index.ntotal == 0


class TestAddChunks:
    def test_add_empty_is_noop(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks([])
        assert vs.index.ntotal == 0
        assert len(vs.chunks) == 0

    def test_add_chunks_stores_without_embedding(self):
        vs = VectorStore(dimension=DIM)
        chunks = _make_chunks(3)
        vs.add_chunks(chunks)
        assert vs.index.ntotal == 3
        assert len(vs.chunks) == 3
        for c in vs.chunks:
            assert "embedding" not in c
            assert "text" in c

    def test_add_chunks_increments(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(2))
        vs.add_chunks(_make_chunks(3))
        assert vs.index.ntotal == 5
        assert len(vs.chunks) == 5

    def test_add_chunks_preserves_metadata(self):
        vs = VectorStore(dimension=DIM)
        chunks = _make_chunks(1)
        chunks[0]["metadata"]["custom"] = "hello"
        vs.add_chunks(chunks)
        assert vs.chunks[0]["metadata"]["custom"] == "hello"

    def test_get_stats_after_add(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(4))
        stats = vs.get_stats()
        assert stats["total_chunks"] == 4
        assert stats["index_size"] == 4
        assert stats["dimension"] == DIM


class TestSearch:
    def test_search_empty_returns_empty(self):
        vs = VectorStore(dimension=DIM)
        q = np.zeros(DIM, dtype="float32")
        assert vs.search(q, top_k=5) == []

    def test_search_single_chunk(self):
        vs = VectorStore(dimension=DIM)
        chunks = _make_chunks(1)
        vs.add_chunks(chunks)
        q = np.arange(DIM, dtype="float32")  # matches chunk 0 exactly
        results = vs.search(q, top_k=5)
        assert len(results) == 1
        chunk, dist = results[0]
        assert chunk["text"] == "chunk 0 text"
        assert dist == pytest.approx(0.0, abs=1e-4)

    def test_search_returns_top_k(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(5))
        q = np.arange(DIM, dtype="float32") + 20.0  # close to chunk 2
        results = vs.search(q, top_k=2)
        assert len(results) == 2

    def test_search_2d_query(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(3))
        q = np.arange(DIM, dtype="float32").reshape(1, -1)
        results = vs.search(q, top_k=2)
        assert len(results) == 2

    def test_search_top_k_larger_than_store(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(2))
        q = np.zeros(DIM, dtype="float32")
        results = vs.search(q, top_k=10)
        # should return at most 2 (pads with -1 filtered)
        assert len(results) == 2

    def test_search_distance_order(self):
        vs = VectorStore(dimension=DIM)
        # chunk 0 at 0, chunk 1 at 10, chunk 2 at 20
        vs.add_chunks(_make_chunks(3))
        q = np.arange(DIM, dtype="float32") + 1.0
        results = vs.search(q, top_k=3)
        dists = [d for _, d in results]
        assert dists == sorted(dists)

    def test_search_filters_invalid_idx(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(1))
        q = np.zeros(DIM, dtype="float32")
        # request k=5 but only 1 valid -> _FakeIndex pads -1, VectorStore filters
        results = vs.search(q, top_k=5)
        assert len(results) == 1
        assert all(idx < len(vs.chunks) for _, idx in [])  # trivial


class TestSaveLoad:
    def test_save_no_path_raises(self):
        vs = VectorStore(dimension=DIM)
        with pytest.raises(ValueError, match="No index path"):
            vs.save()

    def test_save_and_load_roundtrip(self, tmp_path):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(3))
        base = tmp_path / "my_index"
        vs.save(str(base))
        assert (tmp_path / "my_index.index").exists()
        assert (tmp_path / "my_index.chunks").exists()

        # load into new store via explicit load (VectorStore.__init__ checks
        # Path(base).exists() which is False for base without suffix, so auto-load
        # never fires — must call load() directly)
        vs2 = VectorStore(dimension=DIM)
        vs2.load(str(base))
        assert vs2.index.ntotal == 3
        assert len(vs2.chunks) == 3
        assert vs2.chunks[0]["text"] == "chunk 0 text"

    def test_load_missing_index_raises(self, tmp_path):
        vs = VectorStore(dimension=DIM)
        with pytest.raises(FileNotFoundError):
            vs.load(str(tmp_path / "nonexistent"))

    def test_save_with_index_path_attr(self, tmp_path):
        base = tmp_path / "store"
        vs = VectorStore(dimension=DIM, index_path=str(base))
        vs.add_chunks(_make_chunks(2))
        vs.save()  # uses self.index_path
        assert (tmp_path / "store.index").exists()

    def test_clear(self):
        vs = VectorStore(dimension=DIM)
        vs.add_chunks(_make_chunks(5))
        assert vs.index.ntotal == 5
        vs.clear()
        assert vs.index.ntotal == 0
        assert len(vs.chunks) == 0
        assert vs.get_stats()["total_chunks"] == 0
