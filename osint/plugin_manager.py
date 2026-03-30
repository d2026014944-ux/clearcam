from __future__ import annotations

from typing import Any, Dict, List

from .base_plugin import OSINTPlugin


class OSINTPluginManager:
    def __init__(self):
        self.plugins: Dict[str, OSINTPlugin] = {}

    def register(self, plugin: OSINTPlugin):
        self.plugins[plugin.name] = plugin

    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        plugin_results: List[Dict[str, Any]] = []
        for name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            try:
                plugin_results.append({"plugin": name, "result": plugin.enrich_event(event), "ok": True})
            except Exception as e:
                plugin_results.append({"plugin": name, "ok": False, "error": str(e)})

        score_values = [
            p["result"].get("score")
            for p in plugin_results
            if p.get("ok") and isinstance(p.get("result", {}).get("score"), (float, int))
        ]
        blended_score = sum(score_values) / len(score_values) if score_values else 0.0
        return {
            "plugins": plugin_results,
            "blended_score": round(float(blended_score), 4),
            "plugin_count": len(plugin_results),
        }

    def health(self) -> Dict[str, Any]:
        return {
            "plugins": {
                name: plugin.health() for name, plugin in self.plugins.items()
            }
        }
