"""Offline unit tests for backend/generators/ai_client.py — Ollama AIClient.

All tests are synthetic/offline — no Ollama server, no network.
ollama.Client and config.settings are mocked; module is loaded directly
to avoid triggering backend/config.py SECRET_KEY requirement.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Mock dependencies before importing ai_client
# ---------------------------------------------------------------------------
mock_ollama = MagicMock()
mock_client_cls = MagicMock()
mock_ollama.Client = mock_client_cls


class _FakeResponseError(Exception):
    def __init__(self, msg="error"):
        super().__init__(msg)
        self.error = msg


mock_ollama.ResponseError = _FakeResponseError

sys.modules["ollama"] = mock_ollama

# Fake config.settings
fake_settings = MagicMock()
fake_settings.ollama_base_url = "http://localhost:11434"
fake_settings.ollama_model = "llama3.2"
fake_settings.ollama_model_fallback_1 = None
fake_settings.ollama_model_fallback_2 = None
fake_settings.temperature = 0.7

mock_config = MagicMock()
mock_config.settings = fake_settings
sys.modules["config"] = mock_config

# ---------------------------------------------------------------------------
# Load ai_client directly without triggering package __init__
# ---------------------------------------------------------------------------
_spec = importlib.util.spec_from_file_location(
    "ai_client_under_test",
    Path(__file__).parent.parent / "backend" / "generators" / "ai_client.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AIClient = _mod.AIClient
get_ai_client = _mod.get_ai_client


@pytest.fixture(autouse=True)
def _reset_settings():
    """Reset fake_settings and singleton before each test."""
    fake_settings.ollama_base_url = "http://localhost:11434"
    fake_settings.ollama_model = "llama3.2"
    fake_settings.ollama_model_fallback_1 = None
    fake_settings.ollama_model_fallback_2 = None
    fake_settings.temperature = 0.7
    _mod._ai_client_instance = None
    mock_client_cls.reset_mock()
    mock_client_cls.side_effect = None
    yield
    _mod._ai_client_instance = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_client_with_responses(responses):
    """Create a mock Client instance whose chat() returns/pops from responses."""
    inst = MagicMock()

    # responses can be list of either dict returns or exceptions to raise
    def _chat(**kwargs):
        item = responses.pop(0) if responses else {"message": {"content": "ok"}}
        if isinstance(item, Exception):
            raise item
        return item

    inst.chat.side_effect = _chat
    return inst


# ---------------------------------------------------------------------------
# Init tests
# ---------------------------------------------------------------------------
class TestInit:
    def test_provider_and_base_url(self):
        inst = MagicMock()
        mock_client_cls.return_value = inst
        c = AIClient()
        assert c.provider == "ollama"
        assert c.base_url == "http://localhost:11434"
        mock_client_cls.assert_called_once_with(host="http://localhost:11434")

    def test_models_no_fallback(self):
        mock_client_cls.return_value = MagicMock()
        c = AIClient()
        assert c.models == ["llama3.2"]

    def test_models_one_fallback(self):
        fake_settings.ollama_model_fallback_1 = "mistral"
        mock_client_cls.return_value = MagicMock()
        c = AIClient()
        assert c.models == ["llama3.2", "mistral"]

    def test_models_two_fallbacks(self):
        fake_settings.ollama_model_fallback_1 = "mistral"
        fake_settings.ollama_model_fallback_2 = "qwen2"
        mock_client_cls.return_value = MagicMock()
        c = AIClient()
        assert c.models == ["llama3.2", "mistral", "qwen2"]

    def test_init_client_failure_raises(self):
        mock_client_cls.side_effect = RuntimeError("conn fail")
        with pytest.raises(RuntimeError, match="conn fail"):
            AIClient()

    def test_init_uses_custom_base_url(self):
        fake_settings.ollama_base_url = "http://custom:9999"
        mock_client_cls.return_value = MagicMock()
        c = AIClient()
        assert c.base_url == "http://custom:9999"
        mock_client_cls.assert_called_once_with(host="http://custom:9999")


# ---------------------------------------------------------------------------
# generate tests
# ---------------------------------------------------------------------------
class TestGenerate:
    def test_generate_basic_success(self):
        inst = _make_client_with_responses([{"message": {"content": "hello"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate("hi")
        assert out == "hello"
        kwargs = inst.chat.call_args[1]
        assert kwargs["model"] == "llama3.2"
        assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
        assert kwargs["options"]["temperature"] == 0.7

    def test_generate_with_system_message(self):
        inst = _make_client_with_responses([{"message": {"content": "ok"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        c.generate("prompt", system_message="sys")
        kwargs = inst.chat.call_args[1]
        assert kwargs["messages"][0] == {"role": "system", "content": "sys"}
        assert kwargs["messages"][1]["content"] == "prompt"

    def test_generate_temperature_override(self):
        inst = _make_client_with_responses([{"message": {"content": "ok"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        c.generate("p", temperature=0.2)
        assert inst.chat.call_args[1]["options"]["temperature"] == 0.2

    def test_generate_max_tokens_sets_num_predict(self):
        inst = _make_client_with_responses([{"message": {"content": "ok"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        c.generate("p", max_tokens=256)
        assert inst.chat.call_args[1]["options"]["num_predict"] == 256

    def test_generate_no_max_tokens_no_num_predict(self):
        inst = _make_client_with_responses([{"message": {"content": "ok"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        c.generate("p")
        assert "num_predict" not in inst.chat.call_args[1]["options"]

    def test_generate_json_mode_adds_format(self):
        inst = _make_client_with_responses([{"message": {"content": '{"a":1}'}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate("p", json_mode=True)
        assert out == '{"a":1}'
        assert inst.chat.call_args[1]["format"] == "json"

    def test_generate_json_mode_false_no_format(self):
        inst = _make_client_with_responses([{"message": {"content": "ok"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        c.generate("p", json_mode=False)
        assert "format" not in inst.chat.call_args[1]

    def test_generate_empty_response_triggers_fallback_then_success(self):
        fake_settings.ollama_model_fallback_1 = "fallback"
        # first returns empty content -> ValueError -> fallback, second succeeds
        inst = MagicMock()
        inst.chat.side_effect = [
            {"message": {"content": ""}},
            {"message": {"content": "recovered"}},
        ]
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate("p")
        assert out == "recovered"
        assert inst.chat.call_count == 2
        assert inst.chat.call_args_list[1][1]["model"] == "fallback"

    def test_generate_fallback_on_not_found(self):
        fake_settings.ollama_model_fallback_1 = "fallback"
        inst = MagicMock()
        inst.chat.side_effect = [
            _FakeResponseError("model not found"),
            {"message": {"content": "fallback ok"}},
        ]
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate("p")
        assert out == "fallback ok"
        assert inst.chat.call_count == 2

    def test_generate_fallback_on_generic_exception(self):
        fake_settings.ollama_model_fallback_1 = "fallback"
        inst = MagicMock()
        inst.chat.side_effect = [
            RuntimeError("network down"),
            {"message": {"content": "ok2"}},
        ]
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate("p")
        assert out == "ok2"

    def test_generate_all_fail_raises_runtime(self):
        fake_settings.ollama_model_fallback_1 = "f1"
        inst = MagicMock()
        inst.chat.side_effect = [
            _FakeResponseError("not found"),
            RuntimeError("also fail"),
        ]
        mock_client_cls.return_value = inst
        c = AIClient()
        with pytest.raises(RuntimeError, match="All AI models failed"):
            c.generate("p")

    def test_generate_single_model_fail_raises(self):
        inst = MagicMock()
        inst.chat.side_effect = RuntimeError("boom")
        mock_client_cls.return_value = inst
        c = AIClient()
        with pytest.raises(RuntimeError, match="All AI models failed"):
            c.generate("p")


# ---------------------------------------------------------------------------
# generate_with_context
# ---------------------------------------------------------------------------
class TestGenerateWithContext:
    def test_builds_prompt_and_system(self):
        inst = _make_client_with_responses([{"message": {"content": "done"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate_with_context("write intro", "my context", max_tokens=100, temperature=0.5)
        assert out == "done"
        kwargs = inst.chat.call_args[1]
        # system_message should be academic writer
        assert "expert academic writer" in kwargs["messages"][0]["content"]
        # user prompt should embed context and task
        user_content = kwargs["messages"][1]["content"]
        assert "my context" in user_content
        assert "write intro" in user_content
        assert user_content.startswith("Reference Context:")
        assert kwargs["options"]["temperature"] == 0.5
        assert kwargs["options"]["num_predict"] == 100

    def test_context_empty_still_works(self):
        inst = _make_client_with_responses([{"message": {"content": "x"}}])
        mock_client_cls.return_value = inst
        c = AIClient()
        out = c.generate_with_context("task", "")
        assert out == "x"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
class TestSingleton:
    def test_get_ai_client_singleton(self):
        mock_client_cls.return_value = MagicMock()
        a = get_ai_client()
        b = get_ai_client()
        assert a is b
        assert mock_client_cls.call_count == 1

    def test_get_ai_client_new_after_reset(self):
        mock_client_cls.return_value = MagicMock()
        a = get_ai_client()
        _mod._ai_client_instance = None
        mock_client_cls.return_value = MagicMock()
        b = get_ai_client()
        assert a is not b
