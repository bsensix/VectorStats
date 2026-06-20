"""Dashboard tab state machine controller."""

from __future__ import annotations

from vectorstats_v2.core.template_engine import render_template


class DashboardController:
    def __init__(self, session_state: object | None = None) -> None:
        self.session_state = session_state if session_state is not None else {}
        self.state = "empty"
        self.last_layer_id = ""
        self.last_filters: dict[str, object] = {}
        self.last_template_id = ""

    def _session_set(self, key: str, value: object) -> None:
        setter = getattr(self.session_state, "set", None)
        if callable(setter):
            setter(key, value)
            return
        if isinstance(self.session_state, dict):
            self.session_state[key] = value

    def on_generate(
        self,
        context: dict[str, object],
        template_id: str,
        params: dict[str, object],
    ) -> dict[str, object]:
        if not context:
            self.state = "error"
            return {
                "state": self.state,
                "code": "CTX_001_NO_LAYER",
                "message": "No analytical context available.",
            }

        self.state = "loading"
        rendered = render_template(
            template_id=template_id, context=context, params=params
        )
        context_version = str(context.get("context_version", ""))
        if context_version:
            self._session_set("active_context_version", context_version)

        self.state = "success"
        return {
            "state": self.state,
            "code": None,
            "context_version": context_version,
            "payload": rendered,
        }

    def apply_saved_state(self, saved_state: dict[str, object]) -> None:
        self.last_layer_id = str(saved_state.get("layer_id", ""))
        raw_filters = saved_state.get("filters", {})
        self.last_filters = raw_filters if isinstance(raw_filters, dict) else {}
        self.last_template_id = str(saved_state.get("template_id", ""))


__all__ = ["DashboardController"]
