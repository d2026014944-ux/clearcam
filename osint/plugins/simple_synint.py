from __future__ import annotations

from typing import Any, Dict

from ..base_plugin import OSINTPlugin


class SimpleSYNINTPlugin(OSINTPlugin):
    """Lightweight local scoring to avoid blocking the video path."""

    name = "synint_local"

    def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        class_id = int(event.get("class_id", -1))
        score = 0.2
        tags = []

        if class_id == 0:
            score += 0.4
            tags.append("person")
        if class_id in {2, 3, 5, 7}:
            score += 0.3
            tags.append("vehicle")
        if event.get("zone_alert"):
            score += 0.15
            tags.append("zone")
        if event.get("is_notif"):
            score += 0.15
            tags.append("push")

        return {
            "provider": self.name,
            "score": min(score, 0.99),
            "tags": tags,
            "summary": "Local heuristic SYNINT score",
        }
