import pandas as pd, random
from datetime import datetime, timedelta

random.seed(42)

# Failure codes mapped to realistic root causes
FAILURE_CAUSES = {
    "insufficient_funds": 0.30,
    "card_expired":       0.20,
    "bank_downtime":      0.15,
    "risk_blocked":       0.05,
    "otp_timeout":        0.15,
    "network_error":      0.15,
}

def make_record(i):
    amount = random.choice([99, 199, 299, 499, 999, 1499, 2499])
    failed = random.random() < 0.45
    cause = random.choices(list(FAILURE_CAUSES), weights=list(FAILURE_CAUSES.values()))[0] if failed else None
    return {
        "txn_id": f"pay_{i:05d}",
        "customer_id": f"cust_{random.randint(1,120):04d}",
        "amount": amount,
        "method": random.choice(["card", "upi", "netbanking"]),
        "status": "failed" if failed else "success",
        "failure_code": cause,
        "retry_count": random.randint(0, 2) if failed else 0,
        "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
    }

rows = [make_record(i) for i in range(300)]
pd.DataFrame(rows).to_csv("batch.csv", index=False)
print(f"Generated {len(rows)} records -> batch.csv")
