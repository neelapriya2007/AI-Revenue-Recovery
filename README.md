# Reclaim — AI Revenue Recovery Agent
Razorpay AI Buildathon 2026 · Track 03: AI Revenue Recovery

Reclaim detects revenue at risk across a batch of payments/subscriptions,
diagnoses the root cause, executes a *bounded* recovery workflow, and produces
a measured "money recovered" report with a full audit trail.

## The loop
DETECT -> DIAGNOSE -> ACT -> (measure) -> STOP or ESCALATE

Every action is bounded: max 3 recovery attempts, then the case escalates
to a human queue. Every decision is written to `audit_log.jsonl`.

## Run
    pip install -r requirements.txt
    python generate_data.py        # creates synthetic batch (~300 records)
    python agent.py                # runs recovery, writes audit_log.jsonl
    python report.py               # prints money-recovered metrics

## Files
- `generate_data.py` — synthetic payments + subscriptions, no external APIs
- `agent.py`         — the recovery agent (detect/diagnose/act/stop)
- `report.py`        — measured money recovered across the batch
- `audit_log.jsonl`  — one JSON line per agent decision (the audit trail)
