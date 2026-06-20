"""Base contracts shared by VectorStats v2 modules."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnalyticalContext:
    context_id: str = ""
    context_version: str = ""
    layer_id: str = ""
    selected_fields: list[str] = field(default_factory=list)
    filters: dict[str, object] = field(default_factory=dict)
    selection_mode: str = "all"
    summary_stats: dict[str, float | int | None] = field(default_factory=dict)
    sample_rows: list[dict[str, object]] = field(default_factory=list)
    field_profile: dict[str, object] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.context_version.startswith("ctx-"):
            raise ValueError("context_version must start with 'ctx-'")


ERROR_CODE_REGISTRY = {
    "CTX_001_NO_LAYER",
    "CTX_002_INVALID_FIELD",
    "CTX_003_EMPTY_FILTER_RESULT",
    "CTX_004_GEOMETRY_INCONSISTENT",
    "ANL_001_INCOMPATIBLE_FIELD_TYPE",
    "ANL_002_INSUFFICIENT_POINTS",
    "AI_401_KEY_INVALID",
    "AI_408_TIMEOUT",
    "AI_429_RATE_LIMIT",
    "AI_5XX_UPSTREAM",
    "INS_001_MISSING_SECTION",
    "INS_002_PARSE_FAILURE",
}


@dataclass(frozen=True)
class StandardizedError:
    code: str
    message: str
    is_blocking: bool
    recommended_action: str
    telemetry_event: str


__all__ = ["AnalyticalContext", "ERROR_CODE_REGISTRY", "StandardizedError"]
