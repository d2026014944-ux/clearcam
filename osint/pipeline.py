from __future__ import annotations

import queue
import threading
import time
import uuid
from typing import Any, Dict, Optional

from .plugin_manager import OSINTPluginManager
from .plugins.osintgpt_adapter import OSINTGPTAdapterPlugin
from .plugins.simple_synint import SimpleSYNINTPlugin


class OSINTPipeline:
    def __init__(self, database, max_queue_size: int = 2048):
        self.database = database
        self.manager = OSINTPluginManager()
        self.manager.register(SimpleSYNINTPlugin())
        self.manager.register(OSINTGPTAdapterPlugin())

        self.queue: queue.Queue[Dict[str, Any]] = queue.Queue(maxsize=max_queue_size)
        self.stop_event = threading.Event()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True, name="OSINTWorker")
        self.worker.start()

    def enqueue_event(self, event: Dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        payload = {
            "job_id": job_id,
            "event": event,
            "status": "queued",
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self.database.run_put("osint_jobs", job_id, payload)
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            payload["status"] = "dropped"
            payload["updated_at"] = time.time()
            payload["error"] = "queue_full"
            self.database.run_put("osint_jobs", job_id, payload)
        return job_id

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                payload = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            job_id = payload["job_id"]
            try:
                payload["status"] = "processing"
                payload["updated_at"] = time.time()
                self.database.run_put("osint_jobs", job_id, payload)

                result = self.manager.enrich(payload["event"])
                result_record = {
                    "job_id": job_id,
                    "event": payload["event"],
                    "status": "pending_review",
                    "created_at": payload["created_at"],
                    "updated_at": time.time(),
                    "result": result,
                    "action": None,
                }
                self.database.run_put("osint_results", job_id, result_record)

                payload["status"] = "completed"
                payload["updated_at"] = time.time()
                self.database.run_put("osint_jobs", job_id, payload)
            except Exception as e:
                payload["status"] = "failed"
                payload["updated_at"] = time.time()
                payload["error"] = str(e)
                self.database.run_put("osint_jobs", job_id, payload)
            finally:
                self.queue.task_done()

    def list_results(self, cam_name: Optional[str] = None, status: Optional[str] = None):
        all_results = self.database.run_get("osint_results", None)
        if not isinstance(all_results, dict):
            return []
        rows = []
        for _, v in all_results.items():
            row = v if isinstance(v, dict) and "job_id" in v else None
            if row is None:
                continue
            if cam_name and row.get("event", {}).get("cam_name") != cam_name:
                continue
            if status and row.get("status") != status:
                continue
            rows.append(row)
        rows.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return rows

    def get_status(self) -> Dict[str, Any]:
        return {
            "queue_size": self.queue.qsize(),
            "worker_alive": self.worker.is_alive(),
            "plugins": self.manager.health(),
        }

    def apply_action(self, job_id: str, action: str, reason: Optional[str] = None):
        row = self.database.run_get("osint_results", job_id)
        if not row:
            return None
        row["status"] = "confirmed" if action == "confirm" else "dismissed"
        row["action"] = {
            "action": action,
            "reason": reason,
            "ts": time.time(),
        }
        row["updated_at"] = time.time()
        self.database.run_put("osint_results", job_id, row)
        self.database.run_put("osint_actions", job_id, row["action"], replace=False)
        return row

    def shutdown(self):
        self.stop_event.set()
