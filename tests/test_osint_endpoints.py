import json

from clearcam import HLSRequestHandler


class FakeOSINT:
    def __init__(self):
        self.status = {
            "queue_size": 3,
            "worker_alive": True,
            "plugins": {"plugins": {}},
        }
        self.rows = [{"job_id": "a", "event": {"cam_name": "cam1"}, "status": "pending_review"}]
        self.updated = {"job_id": "a", "status": "confirmed"}

    def get_status(self):
        return dict(self.status)

    def list_results(self, cam_name=None, status=None):
        return list(self.rows)

    def apply_action(self, job_id, action, reason=None):
        if job_id != "a":
            return None
        out = dict(self.updated)
        out["action"] = {"action": action, "reason": reason}
        return out


class FakeHandler:
    def __init__(self, osint):
        self.osint = osint
        self.last_200 = None
        self.last_error = None

    def send_200(self, body=None):
        self.last_200 = body

    def send_error(self, code, message=None):
        self.last_error = {"code": code, "message": message}


def test_osint_status_enabled_response():
    h = FakeHandler(FakeOSINT())
    HLSRequestHandler._handle_get_osint_status(h)

    assert h.last_error is None
    assert h.last_200["enabled"] is True
    assert h.last_200["queue_size"] == 3


def test_osint_results_disabled_response():
    h = FakeHandler(None)
    HLSRequestHandler._handle_get_osint_results(h, query={}, cam_name=None)

    assert h.last_error is None
    assert h.last_200 == {"results": [], "count": 0, "enabled": False}


def test_osint_results_pagination_and_filters():
    osint = FakeOSINT()
    osint.rows = [
        {"job_id": "1", "event": {"cam_name": "cam1"}, "status": "pending_review"},
        {"job_id": "2", "event": {"cam_name": "cam1"}, "status": "pending_review"},
    ]
    h = FakeHandler(osint)
    query = {"start": ["1"], "count": ["1"], "status": ["pending_review"]}

    HLSRequestHandler._handle_get_osint_results(h, query=query, cam_name="cam1")

    assert h.last_error is None
    assert h.last_200["enabled"] is True
    assert h.last_200["count"] == 1
    assert h.last_200["results"][0]["job_id"] == "2"


def test_osint_alert_action_invalid_payload():
    h = FakeHandler(FakeOSINT())
    bad = json.dumps({"job_id": "a", "action": "oops"})

    HLSRequestHandler._handle_post_osint_alert_action(h, raw_body=bad.encode("utf-8"))

    assert h.last_200 is None
    assert h.last_error["code"] == 400


def test_osint_alert_action_success():
    h = FakeHandler(FakeOSINT())
    body = json.dumps({"job_id": "a", "action": "confirm", "reason": "ok"})

    HLSRequestHandler._handle_post_osint_alert_action(h, raw_body=body.encode("utf-8"))

    assert h.last_error is None
    assert h.last_200["status"] == "ok"
    assert h.last_200["result"]["status"] == "confirmed"


def test_health_handler_response():
    h = FakeHandler(FakeOSINT())

    HLSRequestHandler._handle_get_health(h)

    assert h.last_error is None
    assert h.last_200["status"] == "ok"
    assert h.last_200["service"] == "clearcam"
