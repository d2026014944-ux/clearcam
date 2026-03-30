from __future__ import annotations

import os
from typing import Any, Dict

from ..base_plugin import OSINTPlugin


class OSINTGPTAdapterPlugin(OSINTPlugin):
    """Adapter placeholder for osintgpt/OpenAI-driven analysis.

    This keeps MVP safe and optional: if no API key is available,
    the plugin returns a passive result instead of failing jobs.
    """

    name = "osintgpt_adapter"

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.api_key = os.getenv("OPENAI_API_KEY")

    def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "provider": self.name,
                "score": 0.0,
                "summary": "OPENAI_API_KEY not configured; adapter running in passive mode",
                "mode": "passive",
            }

        cam_name = event.get("cam_name", "unknown")
        class_id = event.get("class_id", "unknown")
        return {
            "provider": self.name,
            "score": 0.5,
            "summary": f"Stubbed GPT enrichment for cam={cam_name}, class={class_id}",
            "mode": "stub",
        }
