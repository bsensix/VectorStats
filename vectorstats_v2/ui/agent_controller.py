"""Agent tab state machine controller."""

from __future__ import annotations

from vectorstats_v2.core.insight_formatter import format_narrative


class AgentController:
    def __init__(
        self,
        session_state: object | None = None,
        agent_client: object | None = None,
    ) -> None:
        self.session_state = session_state if session_state is not None else {}
        self.agent_client = agent_client
        self.state = "empty"
        self.cancel_requested = False
        self.recent_queries: list[str] = []
        self.ask_enabled = False
        self.last_error_code: str | None = None

    def _session_set(self, key: str, value: object) -> None:
        setter = getattr(self.session_state, "set", None)
        if callable(setter):
            setter(key, value)
            return
        if isinstance(self.session_state, dict):
            self.session_state[key] = value

    def request_cancel(self) -> None:
        self.cancel_requested = True

    def on_ask(
        self,
        prompt: str,
        context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        _ = prompt
        if not context:
            self.state = "error"
            self.last_error_code = "CTX_001_NO_LAYER"
            return {
                "state": self.state,
                "code": "CTX_001_NO_LAYER",
                "message": "Build context before requesting insights.",
            }

        self.state = "loading"
        if self.cancel_requested:
            self.cancel_requested = False
            self.state = "error"
            self.last_error_code = "AI_408_TIMEOUT"
            return {
                "state": self.state,
                "code": "AI_408_TIMEOUT",
                "message": "Request cancelled by user.",
            }

        if not self.ask_enabled:
            self.state = "error"
            self.last_error_code = "AI_401_KEY_INVALID"
            return {
                "state": self.state,
                "code": "AI_401_KEY_INVALID",
                "message": "Update and validate your OpenAI API key.",
            }

        context_version = str(context.get("context_version", ""))
        if context_version:
            self._session_set("active_context_version", context_version)

        if self.agent_client is not None and hasattr(self.agent_client, "generate"):
            generated_text = str(
                self.agent_client.generate(context=context, prompt=prompt)
            )
        else:
            generated_text = "Diagnostic: local summary only."

        formatted = format_narrative(generated_text)

        self.state = "success"
        self.last_error_code = None
        return {
            "state": self.state,
            "code": None,
            "context_version": context_version,
            "insight": generated_text,
            "narrative": formatted.blocks,
            "narrative_error": formatted.error_code,
        }

    def validate_api_key(self, api_key: str) -> bool:
        normalized = api_key.strip()
        is_valid = normalized.startswith("sk-") and len(normalized) >= 12
        self.ask_enabled = is_valid
        self.last_error_code = None if is_valid else "AI_401_KEY_INVALID"
        return is_valid

    def apply_saved_state(self, saved_state: dict[str, object]) -> None:
        raw_queries = saved_state.get("recent_queries", [])
        if isinstance(raw_queries, list):
            self.recent_queries = [str(query) for query in raw_queries]
        else:
            self.recent_queries = []


__all__ = ["AgentController"]
