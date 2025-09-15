# tests/test_payment.py
from fastapi.testclient import TestClient
from app.main import app, DATA, PAYMENTS_FILE, ACCOUNTS_FILE

client = TestClient(app)

def reset_data():
    # Clean JSON files between tests so runs are isolated
    if PAYMENTS_FILE.exists():
        PAYMENTS_FILE.unlink()
    if ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.unlink()
    DATA.mkdir(parents=True, exist_ok=True)

def test_health_ok():
    reset_data()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_payment_and_settlement_flow():
    reset_data()
    # 1) create two payments for same account
    p1 = {"user": "alice", "amount": 100.5, "method": "upi", "account_id": "acct_demo"}
    p2 = {"user": "bob",   "amount": 200.0, "method": "credit_card", "account_id": "acct_demo"}
    r1 = client.post("/payment", json=p1); assert r1.status_code == 200
    r2 = client.post("/payment", json=p2); assert r2.status_code == 200

    # 2) list payments for today's IST date
    today = r1.json()["date_ist"]
    r = client.get(f"/payments?account_id=acct_demo&date_str={today}")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    total = round(sum(p["amount"] for p in items), 2)
    assert total == 300.5

    # 3) settle and verify summary
    r = client.post("/accounts/acct_demo/settle", json={"date": today})
    assert r.status_code == 200
    s = r.json()
    assert s["total_payments"] == 2
    assert round(s["total_amount"], 2) == 300.5

    # 4) balance and ledger reflect settlement
    r = client.get("/accounts/acct_demo/balance")
    assert r.status_code == 200
    assert round(r.json()["balance"], 2) == 300.5

    r = client.get("/accounts/acct_demo/ledger")
    assert r.status_code == 200
    ledger = r.json()["ledger"]
    assert any(e.get("type") == "daily_settlement" and e.get("date") == today for e in ledger)
