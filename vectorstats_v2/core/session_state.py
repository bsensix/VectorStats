"""Session-level state used by context lifecycle hooks."""

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class SessionState:
    hard_invalidated: bool = False
    values: dict[str, object] = field(default_factory=dict)
    path: Path | None = None

    def on_edit_committed(self) -> None:
        self.hard_invalidated = True

    def clear_hard_invalidation(self) -> None:
        self.hard_invalidated = False

    def set(self, key: str, value: object) -> None:
        self.values[key] = value

    def get(self, key: str, default: object | None = None) -> object | None:
        return self.values.get(key, default)

    def save(self, payload: dict[str, object]) -> None:
        self.values.update(payload)
        if self.path is None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.values, ensure_ascii=True, indent=2), encoding="utf-8"
        )

    def load(self) -> dict[str, object]:
        if self.path is not None and self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self.values.update(data)
        return dict(self.values)


__all__ = ["SessionState"]
