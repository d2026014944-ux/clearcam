import time

from osint.pipeline import OSINTPipeline


class FakeDB:
    def __init__(self):
        self.tables = {}

    def run_put(self, table, key, val=None, id=None, replace=True, timeout=5):
        store = self.tables.setdefault(table, {})
        store[key] = val
        return val

    def run_get(self, table, key=None, id=None, timeout=5):
        store = self.tables.get(table, {})
        if key is None:
            return store
        return store.get(key, {})

    def run_delete(self, table, key, id=None, timeout=5):
        store = self.tables.get(table, {})
        store.pop(key, None)
        return True


def wait_until(condition, timeout=2.0):
    start = time.time()
    while time.time() - start < timeout:
        if condition():
            return True
        time.sleep(0.05)
    return False


def test_pipeline_processes_event_and_creates_result():
    db = FakeDB()
    pipeline = OSINTPipeline(db)

    job_id = pipeline.enqueue_event(
        {
            "cam_name": "cam1",
            "class_id": 0,
            "zone_alert": True,
            "is_notif": True,
        }
    )

    assert wait_until(lambda: db.run_get("osint_jobs", job_id).get("status") == "completed")
    result = db.run_get("osint_results", job_id)
    assert result["job_id"] == job_id
    assert result["status"] == "pending_review"
    assert "result" in result

    pipeline.shutdown()


def test_pipeline_action_confirm_updates_status_and_audit():
    db = FakeDB()
    pipeline = OSINTPipeline(db)

    job_id = pipeline.enqueue_event({"cam_name": "cam2", "class_id": 2})
    assert wait_until(lambda: db.run_get("osint_jobs", job_id).get("status") == "completed")

    updated = pipeline.apply_action(job_id, "confirm", "validated by analyst")
    assert updated is not None
    assert updated["status"] == "confirmed"
    assert updated["action"]["action"] == "confirm"

    action_log = db.run_get("osint_actions", job_id)
    assert action_log["action"] == "confirm"

    pipeline.shutdown()


def test_pipeline_list_results_filter_by_camera():
    db = FakeDB()
    pipeline = OSINTPipeline(db)

    j1 = pipeline.enqueue_event({"cam_name": "cam_a", "class_id": 0})
    j2 = pipeline.enqueue_event({"cam_name": "cam_b", "class_id": 7})

    assert wait_until(lambda: db.run_get("osint_jobs", j1).get("status") == "completed")
    assert wait_until(lambda: db.run_get("osint_jobs", j2).get("status") == "completed")

    cam_a_rows = pipeline.list_results(cam_name="cam_a")
    assert len(cam_a_rows) == 1
    assert cam_a_rows[0]["event"]["cam_name"] == "cam_a"

    pipeline.shutdown()
