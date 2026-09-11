"""Offline unit tests for backend/extractors — DocumentExtractor dispatch.

All tests are synthetic/offline — no network, no tesseract binary, no real
PDF/DOCX/PPTX parsing needed. Heavy deps (python-docx, PyPDF2, pptx, PIL)
are mocked at import time so tests run with only pytest.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock heavy third-party modules before importing extractors
# ---------------------------------------------------------------------------
for _mod in [
    "docx",
    "docx.enum",
    "docx.enum.style",
    "docx.shared",
    "PyPDF2",
    "pptx",
    "PIL",
    "PIL.Image",
    "pytesseract",
]:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

sys.modules["docx"].Document = MagicMock()
sys.modules["PyPDF2"].PdfReader = MagicMock()
sys.modules["pptx"].Presentation = MagicMock()

from extractors import DocumentExtractor, extract_document  # noqa: E402

_mod = sys.modules["extractors"]


class TestSupportedExtensions:
    def test_supported_map_complete(self):
        exts = DocumentExtractor.SUPPORTED_EXTENSIONS
        for k in [".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".txt"]:
            assert k in exts
        assert exts[".pdf"] == "pdf"
        assert exts[".docx"] == "docx"
        assert exts[".pptx"] == "pptx"
        assert exts[".png"] == "image"

    def test_is_supported_true(self):
        assert DocumentExtractor.is_supported("report.pdf") is True
        assert DocumentExtractor.is_supported("doc.DOCX") is True
        assert DocumentExtractor.is_supported("slides.pptx") is True
        assert DocumentExtractor.is_supported("photo.JPG") is True
        assert DocumentExtractor.is_supported("notes.txt") is True

    def test_is_supported_false(self):
        assert DocumentExtractor.is_supported("archive.zip") is False
        assert DocumentExtractor.is_supported("script.py") is False
        assert DocumentExtractor.is_supported("no_extension") is False

    def test_case_insensitive(self):
        assert DocumentExtractor.is_supported("FILE.PDF") is True
        assert DocumentExtractor.is_supported("FILE.Pdf") is True


class TestExtractText:
    def test_extract_text_reads_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("Hello world\nLine two", encoding="utf-8")
        ext = DocumentExtractor()
        result = ext._extract_text(str(f))
        assert result["text"] == "Hello world\nLine two"
        assert result["headings"] == []
        assert result["sections"] == []
        assert result["images"] == []

    def test_extract_text_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        ext = DocumentExtractor()
        result = ext._extract_text(str(f))
        assert result["text"] == ""

    def test_extract_text_unicode(self, tmp_path):
        f = tmp_path / "uni.txt"
        f.write_text("café — naïve résumé", encoding="utf-8")
        ext = DocumentExtractor()
        result = ext._extract_text(str(f))
        assert "café" in result["text"]


class TestDispatch:
    def _make_tmp(self, tmp_path, name, content="dummy"):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)

    def test_dispatch_txt(self, tmp_path):
        path = self._make_tmp(tmp_path, "doc.txt", "plain text content")
        result = DocumentExtractor().extract(path)
        assert result["text"] == "plain text content"
        assert result["file_info"]["type"] == "text"
        assert result["file_info"]["extension"] == ".txt"

    def test_dispatch_unsupported_raises(self, tmp_path):
        path = self._make_tmp(tmp_path, "archive.zip", "x")
        with pytest.raises(ValueError, match="Unsupported file type"):
            DocumentExtractor().extract(path)

    def test_dispatch_pdf_calls_extract_pdf(self, tmp_path):
        path = self._make_tmp(tmp_path, "doc.pdf", "x")
        fake = {"text": "pdf text", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_pdf", return_value=fake) as mock_pdf:
            result = DocumentExtractor().extract(path)
            mock_pdf.assert_called_once_with(path, None)
            assert result["text"] == "pdf text"
            assert result["file_info"]["type"] == "pdf"

    def test_dispatch_docx_calls_extract_docx(self, tmp_path):
        path = self._make_tmp(tmp_path, "doc.docx", "x")
        fake = {"text": "docx text", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_docx", return_value=fake) as mock_docx:
            result = DocumentExtractor().extract(path)
            mock_docx.assert_called_once_with(path)
            assert result["file_info"]["type"] == "docx"

    def test_dispatch_pptx_calls_extract_pptx(self, tmp_path):
        path = self._make_tmp(tmp_path, "deck.pptx", "x")
        fake = {"text": "pptx text", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_pptx", return_value=fake) as mock_pptx:
            result = DocumentExtractor().extract(path)
            mock_pptx.assert_called_once_with(path)
            assert result["file_info"]["type"] == "pptx"

    def test_dispatch_image_calls_extract_image(self, tmp_path):
        path = self._make_tmp(tmp_path, "photo.png", "x")
        fake = {"text": "ocr text", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_image", return_value=fake) as mock_img:
            result = DocumentExtractor(tesseract_cmd="/usr/bin/tesseract").extract(path)
            mock_img.assert_called_once_with(path, "/usr/bin/tesseract")
            assert result["file_info"]["type"] == "image"

    def test_dispatch_adds_file_info(self, tmp_path):
        path = self._make_tmp(tmp_path, "notes.txt", "hi")
        result = DocumentExtractor().extract(path)
        info = result["file_info"]
        assert info["name"] == "notes.txt"
        assert info["size"] >= 2
        assert info["extension"] == ".txt"

    def test_dispatch_propagates_tesseract_cmd(self, tmp_path):
        path = self._make_tmp(tmp_path, "scan.pdf", "x")
        fake = {"text": "t", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_pdf", return_value=fake) as mock_pdf:
            DocumentExtractor(tesseract_cmd="/custom/tesseract").extract(path)
            mock_pdf.assert_called_once_with(path, "/custom/tesseract")

    def test_dispatch_doc_alias(self, tmp_path):
        path = self._make_tmp(tmp_path, "legacy.doc", "x")
        fake = {"text": "doc text", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_docx", return_value=fake) as mock_docx:
            result = DocumentExtractor().extract(path)
            mock_docx.assert_called_once()
            assert result["file_info"]["type"] == "docx"

    def test_dispatch_jpeg_alias(self, tmp_path):
        path = self._make_tmp(tmp_path, "pic.jpeg", "x")
        fake = {"text": "img", "headings": [], "sections": [], "images": [], "metadata": {}}
        with patch.object(_mod, "extract_image", return_value=fake) as mock_img:
            result = DocumentExtractor().extract(path)
            assert result["file_info"]["type"] == "image"
            mock_img.assert_called_once()

    def test_extract_document_convenience(self, tmp_path):
        path = self._make_tmp(tmp_path, "a.txt", "convenience")
        result = extract_document(str(path))
        assert result["text"] == "convenience"

    def test_dispatch_reraises_extractor_error(self, tmp_path):
        path = self._make_tmp(tmp_path, "bad.pdf", "x")
        with patch.object(_mod, "extract_pdf", side_effect=RuntimeError("parse failed")):
            with pytest.raises(RuntimeError, match="parse failed"):
                DocumentExtractor().extract(path)

    def test_deterministic_dispatch(self, tmp_path):
        path = self._make_tmp(tmp_path, "repeat.txt", "same")
        r1 = DocumentExtractor().extract(path)
        r2 = DocumentExtractor().extract(path)
        assert r1["text"] == r2["text"]
        assert r1["file_info"]["name"] == r2["file_info"]["name"]
