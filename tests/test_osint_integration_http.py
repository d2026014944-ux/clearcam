"""
Testes de integração HTTP para o ciclo completo OSINT:
1. Listar resultados com status pending_review
2. Aplicar ação (confirm/dismiss)
3. Refletir status nos resultados posteriores
"""

import json
import time
from clearcam import HLSRequestHandler


class FakeOSINT:
    """OSINT mock com estado mutável para simular ciclo real"""
    
    def __init__(self):
        self.results_store = {
            "job_1": {
                "job_id": "job_1",
                "event": {
                    "cam_name": "entrance",
                    "class_id": 0,
                    "zone_alert": True,
                    "is_notif": True,
                    "timestamp": int(time.time()) - 300,
                    "thumbnail": "/path/to/thumb.jpg",
                },
                "result": {
                    "blended_score": 0.87,
                    "plugins": ["simple_synint"],
                },
                "status": "pending_review",
                "created_at": time.time() - 600,
                "updated_at": time.time() - 300,
            },
            "job_2": {
                "job_id": "job_2",
                "event": {
                    "cam_name": "entrance",
                    "class_id": 1,
                    "zone_alert": False,
                    "is_notif": True,
                    "timestamp": int(time.time()) - 100,
                    "thumbnail": "/path/to/thumb2.jpg",
                },
                "result": {
                    "blended_score": 0.65,
                    "plugins": ["osintgpt"],
                },
                "status": "pending_review",
                "created_at": time.time() - 400,
                "updated_at": time.time() - 100,
            },
        }
    
    def get_status(self):
        return {
            "queue_size": 0,
            "worker_alive": True,
            "plugins": {"simple_synint": "ok", "osintgpt": "ok"},
        }
    
    def list_results(self, cam_name=None, status=None):
        """Filtra resultados por câmera e status"""
        results = list(self.results_store.values())
        
        if cam_name:
            results = [
                r for r in results
                if r.get("event", {}).get("cam_name") == cam_name
            ]
        
        if status:
            results = [r for r in results if r.get("status") == status]
        
        results.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return results
    
    def apply_action(self, job_id, action, reason=None):
        """Aplica ação e atualiza status no store"""
        if job_id not in self.results_store:
            return None
        
        record = self.results_store[job_id]
        new_status = "confirmed" if action == "confirm" else "dismissed"
        
        record["status"] = new_status
        record["action"] = {
            "action": action,
            "reason": reason,
            "ts": time.time(),
        }
        record["updated_at"] = time.time()
        
        return dict(record)


class FakeHandler:
    """Handler mock que captura respostas HTTP"""
    
    def __init__(self, osint):
        self.osint = osint
        self.last_200 = None
        self.last_error = None
    
    def send_200(self, body=None):
        self.last_200 = body
    
    def send_error(self, code, message=None):
        self.last_error = {"code": code, "message": message}


# ===== TESTES =====

def test_list_pending_review_results_all_cameras():
    """GET /osint_results → listar todos pending_review"""
    osint = FakeOSINT()
    h = FakeHandler(osint)
    
    HLSRequestHandler._handle_get_osint_results(
        h, 
        query={"status": ["pending_review"]},
        cam_name=None
    )
    
    assert h.last_error is None
    assert h.last_200["enabled"] is True
    assert h.last_200["count"] == 2
    assert len(h.last_200["results"]) >= 1
    assert h.last_200["results"][0]["status"] == "pending_review"


def test_list_pending_review_filtered_by_camera():
    """GET /osint_results?cam=entrance&status=pending_review"""
    osint = FakeOSINT()
    h = FakeHandler(osint)
    
    HLSRequestHandler._handle_get_osint_results(
        h,
        query={"status": ["pending_review"]},
        cam_name="entrance"
    )
    
    assert h.last_error is None
    assert h.last_200["enabled"] is True
    
    for row in h.last_200["results"]:
        assert row["event"]["cam_name"] == "entrance"
        assert row["status"] == "pending_review"


def test_confirm_osint_result_cycle():
    """Fluxo: listar → confirmar → verificar status mudou"""
    osint = FakeOSINT()
    
    # Passo 1: Listar pending_review
    h_list1 = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_list1,
        query={"status": ["pending_review"]},
        cam_name=None
    )
    
    initial_count = h_list1.last_200["count"]
    job_to_confirm = h_list1.last_200["results"][0]["job_id"]
    
    assert h_list1.last_error is None
    assert initial_count >= 1
    
    # Passo 2: Confirmar um resultado
    h_action = FakeHandler(osint)
    body = json.dumps({
        "job_id": job_to_confirm,
        "action": "confirm",
        "reason": "test_integration"
    })
    HLSRequestHandler._handle_post_osint_alert_action(h_action, raw_body=body.encode("utf-8"))
    
    assert h_action.last_error is None
    assert h_action.last_200["status"] == "ok"
    assert h_action.last_200["result"]["status"] == "confirmed"
    
    # Passo 3: Listar novamente - resultado deve desaparecer de pending_review
    h_list2 = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_list2,
        query={"status": ["pending_review"]},
        cam_name=None
    )
    
    final_count = h_list2.last_200["count"]
    
    assert h_list2.last_error is None
    assert final_count == initial_count - 1
    
    # Verificar que o job confirmado não está mais em pending_review
    confirmed_jobs = [r["job_id"] for r in h_list2.last_200["results"]]
    assert job_to_confirm not in confirmed_jobs


def test_dismiss_osint_result_cycle():
    """Fluxo: listar → descartar → verificar status mudou"""
    osint = FakeOSINT()
    
    # Passo 1: Listar pending_review
    h_list1 = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_list1,
        query={"status": ["pending_review"]},
        cam_name=None
    )
    
    initial_count = h_list1.last_200["count"]
    job_to_dismiss = h_list1.last_200["results"][0]["job_id"]
    
    # Passo 2: Descartar um resultado
    h_action = FakeHandler(osint)
    body = json.dumps({
        "job_id": job_to_dismiss,
        "action": "dismiss",
        "reason": "false_positive"
    })
    HLSRequestHandler._handle_post_osint_alert_action(h_action, raw_body=body.encode("utf-8"))
    
    assert h_action.last_error is None
    assert h_action.last_200["result"]["status"] == "dismissed"
    assert h_action.last_200["result"]["action"]["reason"] == "false_positive"
    
    # Passo 3: Listar novamente
    h_list2 = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_list2,
        query={"status": ["pending_review"]},
        cam_name=None
    )
    
    final_count = h_list2.last_200["count"]
    
    assert final_count == initial_count - 1
    dismissed_jobs = [r["job_id"] for r in h_list2.last_200["results"]]
    assert job_to_dismiss not in dismissed_jobs


def test_list_confirmed_results():
    """Verificar que resultados confirmados podem ser listados por status=confirmed"""
    osint = FakeOSINT()
    
    # Confirmar um resultado
    h_action = FakeHandler(osint)
    body = json.dumps({"job_id": "job_1", "action": "confirm", "reason": "test"})
    HLSRequestHandler._handle_post_osint_alert_action(h_action, raw_body=body.encode("utf-8"))
    
    assert h_action.last_error is None
    
    # Listar resultados confirmados
    h_list = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_list,
        query={"status": ["confirmed"]},
        cam_name=None
    )
    
    assert h_list.last_error is None
    assert h_list.last_200["count"] >= 1
    
    confirmed_results = h_list.last_200["results"]
    assert all(r["status"] == "confirmed" for r in confirmed_results)
    
    job_ids = [r["job_id"] for r in confirmed_results]
    assert "job_1" in job_ids


def test_action_nonexistent_job_returns_404():
    """POST /osint_alert_action com job_id inválido → 404"""
    osint = FakeOSINT()
    h = FakeHandler(osint)
    
    body = json.dumps({
        "job_id": "nonexistent_job",
        "action": "confirm",
        "reason": None
    })
    HLSRequestHandler._handle_post_osint_alert_action(h, raw_body=body.encode("utf-8"))
    
    assert h.last_200 is None
    assert h.last_error["code"] == 404


def test_pagination_large_result_set():
    """Verificar paginação com muitos resultados"""
    osint = FakeOSINT()
    
    # Adicionar mais resultados
    for i in range(3, 15):
        osint.results_store[f"job_{i}"] = {
            "job_id": f"job_{i}",
            "event": {
                "cam_name": "entrance",
                "class_id": i % 3,
                "timestamp": int(time.time()) - (i * 100),
            },
            "result": {"blended_score": 0.5 + (i * 0.01)},
            "status": "pending_review",
            "updated_at": time.time() - (i * 100),
        }
    
    h = FakeHandler(osint)
    
    # Pedir page 1
    HLSRequestHandler._handle_get_osint_results(
        h,
        query={"start": ["0"], "count": ["5"]},
        cam_name=None
    )
    
    assert h.last_error is None
    assert h.last_200["count"] == 5
    page1_ids = [r["job_id"] for r in h.last_200["results"]]
    
    # Pedir page 2
    h_page2 = FakeHandler(osint)
    HLSRequestHandler._handle_get_osint_results(
        h_page2,
        query={"start": ["5"], "count": ["5"]},
        cam_name=None
    )
    
    assert h_page2.last_error is None
    page2_ids = [r["job_id"] for r in h_page2.last_200["results"]]
    
    # Pages devem ter resultados diferentes
    assert set(page1_ids).isdisjoint(set(page2_ids))
