"""
Tests for the TJ3 microservice.

Health check runs anywhere; schedule tests require tj3 installed locally.
Run the full suite inside Docker: docker compose run --rm microservice pytest tests/
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "tj3_version" in data


# ── /schedule ─────────────────────────────────────────────────────────────────

MINIMAL_TJP = """\
project p1 "Test" 2026-01-01 - 2027-01-01 {
  timezone "UTC"
  now 2026-01-01
  scenario plan "Plan"
}

resource res1 "Developer" {
  workinghours mon 9:00 - 17:00
  workinghours tue 9:00 - 17:00
  workinghours wed 9:00 - 17:00
  workinghours thu 9:00 - 17:00
  workinghours fri 9:00 - 17:00
  workinghours sat off
  workinghours sun off
}

task t1 "Task One" {
  effort 5d
  allocate res1
}

task t2 "Task Two" {
  effort 3d
  allocate res1
  depends !t1
}

taskreport "schedule_plan" {
  formats csv
  columns id, bsi, name, start, end, effort, duration, resources, criticalness
  scenarios plan
}
"""

INVALID_TJP = "this is not valid taskjuggler syntax at all"


def test_schedule_valid_tjp_returns_csv_files():
    resp = client.post("/schedule", json={"tjp_content": MINIMAL_TJP})
    assert resp.status_code == 200
    data = resp.json()
    assert "csv_files" in data
    assert len(data["csv_files"]) > 0


def test_schedule_csv_contains_tasks():
    resp = client.post("/schedule", json={"tjp_content": MINIMAL_TJP})
    assert resp.status_code == 200
    all_csv = "\n".join(resp.json()["csv_files"].values())
    assert "t1" in all_csv or "Task One" in all_csv


def test_schedule_invalid_tjp_returns_422():
    resp = client.post("/schedule", json={"tjp_content": INVALID_TJP})
    assert resp.status_code == 422


def test_schedule_timeout_field_validated():
    # timeout below minimum (10) should be rejected by Pydantic
    resp = client.post("/schedule", json={"tjp_content": MINIMAL_TJP, "timeout": 5})
    assert resp.status_code == 422


def test_schedule_empty_content_rejected():
    resp = client.post("/schedule", json={"tjp_content": ""})
    assert resp.status_code in (422, 422)  # Pydantic or tj3 rejection
