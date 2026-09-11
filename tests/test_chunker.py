"""Offline unit tests for backend/rag/chunker.py — TextChunker core RAG logic.

All tests are synthetic/offline — no network, no FAISS, no embeddings required.
Covers: init, chunk_text, chunk_by_sections, _split_text, _split_sentences, chunk_document.
"""

import importlib.util
import sys
from pathlib import Path

# Load chunker directly without triggering rag/__init__.py (which pulls heavy deps)
_CHUNKER_PATH = Path(__file__).resolve().parents[1] / "backend" / "rag" / "chunker.py"
_spec = importlib.util.spec_from_file_location("rag.chunker", _CHUNKER_PATH)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["rag.chunker"] = _mod
_spec.loader.exec_module(_mod)
TextChunker = _mod.TextChunker
chunk_document = _mod.chunk_document


class TestTextChunkerInit:
    def test_default_params(self):
        c = TextChunker()
        assert c.chunk_size == 800
        assert c.chunk_overlap == 200
        assert c.min_chunk_size == 100

    def test_custom_params(self):
        c = TextChunker(chunk_size=500, chunk_overlap=50, min_chunk_size=10)
        assert c.chunk_size == 500
        assert c.chunk_overlap == 50
        assert c.min_chunk_size == 10


class TestChunkText:
    def test_empty_text_returns_empty(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        assert c.chunk_text("") == []
        assert c.chunk_text("   ") == []

    def test_short_text_single_chunk(self):
        c = TextChunker(chunk_size=500, chunk_overlap=50, min_chunk_size=10)
        text = "This is a short paragraph about machine learning."
        chunks = c.chunk_text(text)
        assert len(chunks) == 1
        assert "machine learning" in chunks[0]["text"]
        assert chunks[0]["metadata"]["chunk_index"] == 0

    def test_long_text_multiple_chunks(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        para = "This is a paragraph with enough content to test chunking. " * 3
        text = "\n\n".join([para] * 6)
        chunks = c.chunk_text(text)
        assert len(chunks) >= 3
        for ch in chunks:
            assert len(ch["text"]) >= c.min_chunk_size

    def test_min_chunk_filter(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=200)
        text = "Short."
        chunks = c.chunk_text(text)
        assert chunks == []  # filtered by min_chunk_size

    def test_chunk_text_with_metadata(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        meta = {"source": "test.pdf", "page": 1}
        chunks = c.chunk_text("Content " * 30, metadata=meta)
        assert chunks[0]["metadata"]["source"] == "test.pdf"
        assert "chunk_index" in chunks[0]["metadata"]

    def test_overlap_preserved(self):
        c = TextChunker(chunk_size=100, chunk_overlap=30, min_chunk_size=10)
        p1 = "A" * 90
        p2 = "B" * 90
        p3 = "C" * 90
        text = f"{p1}\n\n{p2}\n\n{p3}"
        chunks = c.chunk_text(text)
        # With small chunk_size, we should get multiple chunks
        assert len(chunks) >= 2

    def test_deterministic(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        text = "Deterministic test. " * 50
        a = c.chunk_text(text)
        b = c.chunk_text(text)
        assert len(a) == len(b)
        assert [x["text"] for x in a] == [x["text"] for x in b]


class TestChunkBySections:
    def test_basic_section_chunking(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        sections = [
            {"title": "Introduction", "content": "Intro content " * 20, "level": 1},
            {"title": "Methodology", "content": "Method content " * 20, "level": 1},
        ]
        chunks = c.chunk_by_sections(sections)
        assert len(chunks) >= 2
        titles = {ch["metadata"]["section_title"] for ch in chunks}
        assert "Introduction" in titles
        assert "Methodology" in titles

    def test_empty_content_skipped(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        sections = [
            {"title": "Empty", "content": "", "level": 1},
            {"title": "Valid", "content": "Valid content " * 20, "level": 1},
        ]
        chunks = c.chunk_by_sections(sections)
        assert all(ch["metadata"]["section_title"] != "Empty" for ch in chunks)

    def test_metadata_preserved(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        sections = [
            {"title": "Results", "content": "Results " * 30, "level": 2, "page": 5, "slide": 3}
        ]
        chunks = c.chunk_by_sections(sections)
        assert chunks[0]["metadata"]["section_level"] == 2
        assert chunks[0]["metadata"]["page"] == 5
        assert chunks[0]["metadata"]["slide"] == 3

    def test_min_chunk_filter_sections(self):
        c = TextChunker(chunk_size=200, chunk_overlap=20, min_chunk_size=500)
        sections = [{"title": "Small", "content": "tiny", "level": 1}]
        chunks = c.chunk_by_sections(sections)
        assert chunks == []

    def test_zero_overlap(self):
        c = TextChunker(chunk_size=100, chunk_overlap=0, min_chunk_size=10)
        sections = [
            {"title": "T1", "content": "X " * 100, "level": 1},
        ]
        chunks = c.chunk_by_sections(sections)
        assert len(chunks) >= 1


class TestSplitHelpers:
    def test_split_sentences(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        sentences = c._split_sentences("Hello world. How are you? I am fine!")
        assert len(sentences) == 3
        assert sentences[0] == "Hello world."
        assert sentences[1] == "How are you?"
        assert sentences[2] == "I am fine!"

    def test_split_sentences_strips_empty(self):
        c = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
        sentences = c._split_sentences("  First.   Second.  ")
        assert len(sentences) == 2

    def test_split_text_paragraph_handling(self):
        c = TextChunker(chunk_size=200, chunk_overlap=30, min_chunk_size=10)
        text = "Para one content.\n\nPara two content.\n\nPara three content."
        chunks = c._split_text(text)
        assert len(chunks) >= 1
        # All non-empty paragraphs should appear somewhere
        combined = " ".join(chunks)
        assert "Para one" in combined
        assert "Para two" in combined

    def test_split_text_large_paragraph_sentence_split(self):
        c = TextChunker(chunk_size=80, chunk_overlap=10, min_chunk_size=10)
        # Single paragraph larger than chunk_size — triggers sentence split path
        para = " ".join([f"Sentence {i} is here." for i in range(20)])
        chunks = c._split_text(para)
        assert len(chunks) > 1
        for ch in chunks:
            assert len(ch) > 0


class TestChunkDocument:
    def test_with_sections(self):
        data = {
            "sections": [
                {"title": "Intro", "content": "Intro " * 30, "level": 1},
                {"title": "Methods", "content": "Methods " * 30, "level": 1},
            ]
        }
        chunks = chunk_document(data, chunk_size=100)
        assert len(chunks) >= 2

    def test_fallback_to_text(self):
        data = {"text": "Fallback text " * 40, "metadata": {"source": "doc.pdf"}}
        chunks = chunk_document(data, chunk_size=100)
        assert len(chunks) >= 1
        assert "Fallback" in chunks[0]["text"]

    def test_empty_document(self):
        assert chunk_document({}, chunk_size=100) == []
        assert chunk_document({"text": ""}, chunk_size=100) == []
        assert chunk_document({"sections": []}, chunk_size=100) == []

    def test_chunk_size_respected_param(self):
        data = {"text": "Word " * 200}
        small = chunk_document(data, chunk_size=50)
        large = chunk_document(data, chunk_size=500)
        assert len(small) >= len(large)
