from abc import ABC, abstractmethod
from typing import Any, Dict


class OSINTPlugin(ABC):
    """Contract for enrichment plugins used by the OSINT pipeline."""

    name = "base"

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.enabled = True

    @abstractmethod
    def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Return plugin result payload for one event."""

    def health(self) -> Dict[str, Any]:
        return {"ok": True, "plugin": self.name, "enabled": self.enabled}
