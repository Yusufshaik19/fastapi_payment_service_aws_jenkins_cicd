from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field
from typing import Optional,List,Dict,Any
from pathlib import Path
from datetime import datetime,date
import json,time

app = FastAPI(title="Payment Service (local)")


DATA = Path("data")                               # use a local "data" folder on Windows (no admin rights needed)
DATA.mkdir(parents=True, exist_ok=True)           # create it if missing; don't error if it already exists
PAYMENTS_FILE = DATA / "payments.json"            # file to store a list of payments (append records)
ACCOUNTS_FILE = DATA / "accounts.json"            # file to store account state: {account_id: {balance, ledger: []}}

def _read_json(path: Path, default):              # helper to read JSON or return a default if file missing
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def _write_json(path: Path, obj: Any):            # helper to write pretty JSON (indent=2) for easy inspection
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def iso_date_ist(ts: float | None = None) -> str: # convert a timestamp to YYYY-MM-DD in IST
    try:
        dt = datetime.fromtimestamp(ts or time.time(), ZoneInfo("Asia/Kolkata"))  # use IST timezone
    except Exception:
        dt = datetime.now().astimezone()            # fallback if ZoneInfo unavailable
    return dt.date().isoformat()                    # return date part as 'YYYY-MM-DD'

def _accounts():                                    # load accounts.json and normalize its structure
    state = _read_json(ACCOUNTS_FILE, {})
    for aid, rec in state.items():
        rec.setdefault("balance", 0.0)              # ensure every account has a balance key
        rec.setdefault("ledger", [])                # ensure every account has a ledger list
    return state

class PaymentIn(BaseModel):                         # schema for incoming payment requests
    user: str = Field(..., examples=["alice"])      # required string; example helps /docs
    amount: float = Field(..., gt=0, examples=[499.0])  # required float; must be > 0
    method: str = Field(..., examples=["upi", "credit_card", "netbanking"])  # payment method label
    account_id: str = Field(..., examples=["acct_demo"])  # which account to credit
    ts: Optional[float] = None                      # optional client-supplied timestamp (seconds)

class Payment(PaymentIn):                           # response model extends request with extra fields
    transaction_id: str                             # unique-ish id we assign
    date_ist: str                                   # 'YYYY-MM-DD' (IST) derived from timestamp
    ts: float                                       # server-side timestamp we store

class SettlementIn(BaseModel):                      # request body for settlement
    date: Optional[str] = Field(None, description="YYYY-MM-DD (IST). Defaults to today.")  # which day to settle

app = FastAPI(title="Payment Service (Local)")      # create the FastAPI app (visible in /docs)

@app.get("/health")                                 # GET /health endpoint for liveness/smoke tests
def health():
    return {"status": "ok"}                         # simple JSON response

@app.post("/payment", response_model=Payment)       # POST /payment accepts PaymentIn, returns Payment (validated)
def create_payment(p: PaymentIn):
    payments: List[Dict] = _read_json(PAYMENTS_FILE, [])   # load existing list (or empty)
    ts = float(p.ts) if p.ts else time.time()              # choose client ts if supplied, else now
    txn_id = f"txn_{int(ts)}_{len(payments)+1}"            # simple unique-ish id: timestamp + sequence count
    rec = {                                                # construct the stored record
        "transaction_id": txn_id,
        "user": p.user,
        "amount": float(p.amount),
        "method": p.method,
        "account_id": p.account_id,
        "ts": ts,
        "date_ist": iso_date_ist(ts),                      # normalize to IST day for reporting/settlement
    }
    payments.append(rec)                                   # append to in-memory list
    _write_json(PAYMENTS_FILE, payments)                   # persist to disk
    return rec                                             # FastAPI auto-serializes and validates against Payment

@app.get("/payments")                                      # GET /payments (optionally filter by account/date)
def list_payments(
    account_id: Optional[str] = Query(None),               # ?account_id=... (optional)
    date_str: Optional[str] = Query(None, description="YYYY-MM-DD (IST)")  # ?date_str=... (optional)
):
    payments: List[Dict] = _read_json(PAYMENTS_FILE, [])
    def filt(x: Dict):                                     # inner filter function
        if account_id and x["account_id"] != account_id: return False
        if date_str and x["date_ist"] != date_str: return False
        return True
    return [x for x in payments if filt(x)]                # return filtered list

@app.get("/accounts/{account_id}/balance")                 # GET account balance
def get_balance(account_id: str):
    state = _accounts()
    acct = state.get(account_id, {"balance": 0.0, "ledger": []})  # default if new account
    return {"account_id": account_id, "balance": round(acct["balance"], 2)}  # round for pretty output

@app.get("/accounts/{account_id}/ledger")                  # GET account ledger (settlement history)
def get_ledger(account_id: str):
    state = _accounts()
    acct = state.get(account_id, {"balance": 0.0, "ledger": []})
    return {"account_id": account_id, "ledger": acct["ledger"]}

@app.post("/accounts/{account_id}/settle")                 # POST to settle one day's payments into balance
def settle_day(account_id: str, body: SettlementIn):
    settle_date = body.date or iso_date_ist()              # use provided date or default to "today" (IST)
    try:
        date.fromisoformat(settle_date)                    # validate format 'YYYY-MM-DD'; raise 400 if bad
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")

    payments: List[Dict] = _read_json(PAYMENTS_FILE, [])
    todays = [p for p in payments if p["account_id"] == account_id and p["date_ist"] == settle_date]  # select today's
    total = round(sum(p["amount"] for p in todays), 2)      # sum amounts for that day

    state = _accounts()
    acct = state.setdefault(account_id, {"balance": 0.0, "ledger": []})  # create account if new
    entry = {                                               # ledger entry describing this settlement
        "id": f"set_{settle_date.replace('-','')}_{int(time.time())}",
        "type": "daily_settlement",
        "date": settle_date,
        "count": len(todays),
        "amount": total,
        "at": datetime.now().astimezone().isoformat(),      # timestamp of settlement
    }
    acct["ledger"].append(entry)                            # append audit record
    acct["balance"] = round(acct["balance"] + total, 2)     # increase balance by today's total
    _write_json(ACCOUNTS_FILE, state)                       # persist updated account file

    return {                                                # minimal response summary
        "account_id": account_id,
        "date": settle_date,
        "total_payments": len(todays),
        "total_amount": total,
        "new_balance": acct["balance"],
        "ledger_entry_id": entry["id"]
    }