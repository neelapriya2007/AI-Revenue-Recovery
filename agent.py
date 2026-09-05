"""Reclaim — bounded revenue-recovery agent.

Rules (the 'bounded workflow'):
  - Max 3 recovery attempts per case; then ESCALATE to human queue.
  - Never act on `risk_blocked` (compliance) -> auto-escalate.
  - Recovery probability per intervention is modelled honestly;
    we log what we attempted and what actually recovered.
"""
import json, random, pandas as pd
from datetime import datetime

random.seed(7)
MAX_ATTEMPTS = 3
RECOVERY_PROB = {                 # honest, cause-specific success odds
    "insufficient_funds": 0.28,   # retry on salary day / reminder works
    "card_expired":       0.32,   # update-card link usually converts
    "bank_downtime":      0.34,   # retry after window passes
    "otp_timeout":        0.28,   # nudge + instant retry
    "network_error":      0.50,
}

def choose_action(cause, attempt):
    if cause == "card_expired":       return "send_update_card_link"
    if cause == "bank_downtime":      return "schedule_retry_next_window"
    if cause == "insufficient_funds": return "retry_end_of_month_reminder"
    return "instant_retry_with_nudge"

def log(entry):
    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps({"ts": datetime.now().isoformat(), **entry}) + "\n")

def run_case(row):
    cause = row.failure_code
    attempts, recovered, recovered_amount = 0, False, 0.0
    if cause == "risk_blocked":
        log({"txn": row.txn_id, "decision": "escalate",
             "reason": "compliance_hold", "amount_at_risk": row.amount})
        return {"txn_id": row.txn_id, "cause": cause, "outcome": "escalated",
                "attempts": 0, "recovered_amount": 0.0}
    while attempts < MAX_ATTEMPTS and not recovered:
        attempts += 1
        action = choose_action(cause, attempts)
        log({"txn": row.txn_id, "attempt": attempts, "action": action,
             "cause": cause, "amount_at_risk": row.amount})
        if random.random() < RECOVERY_PROB.get(cause, 0.35):
            recovered, recovered_amount = True, float(row.amount)
            log({"txn": row.txn_id, "attempt": attempts, "action": action,
                 "result": "RECOVERED", "amount_recovered": row.amount})
    outcome = "recovered" if recovered else "escalated"
    if not recovered:
        log({"txn": row.txn_id, "decision": "escalate",
             "reason": "max_attempts_reached", "amount_at_risk": row.amount})
    return {"txn_id": row.txn_id, "cause": cause, "outcome": outcome,
            "attempts": attempts, "recovered_amount": recovered_amount}

def main():
    open("audit_log.jsonl", "w").close()  # fresh audit trail each run
    df = pd.read_csv("batch.csv")
    at_risk = df[df.status == "failed"]
    results = [run_case(r) for r in at_risk.itertuples()]
    pd.DataFrame(results).to_csv("results.csv", index=False)
    print(f"Processed {len(results)} at-risk cases -> results.csv")

if __name__ == "__main__":
    main()
