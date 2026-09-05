# Reclaim — Bounded AI Revenue Recovery Agent

> Reclaim finds revenue that's slipping away and wins it back — with an AI agent that detects revenue at risk, diagnoses the root cause, executes a bounded recovery workflow, and proves every rupee it recovers.

**Razorpay AI Buildathon 2026 · Track 03: AI Revenue Recovery**

---

##  The problem

Revenue loss rarely happens in one clean step. A payment degrades, a card expires, an OTP times out — and most systems either blind-retry once and give up, or spam customers until they churn. That money leaks silently, every single day.

##  The solution

Reclaim runs a **bounded, auditable agent loop** across a batch of payments:

```
DETECT → DIAGNOSE → ACT (max 3 attempts) → STOP / ESCALATE → AUDIT
```

- **Detect** — flags every failed payment as revenue at risk
- **Diagnose** — classifies the root cause (`insufficient_funds`, `card_expired`, `bank_downtime`, `otp_timeout`, `network_error`, `risk_blocked`)
- **Act** — picks the *right* intervention per cause, not a blind retry:
  - `card_expired` → update-card link
  - `insufficient_funds` → salary-day retry reminder
  - `bank_downtime` → retry in the next clean window
  - `otp_timeout` / `network_error` → instant retry with nudge
- **Stop & escalate** — never more than 3 attempts; `risk_blocked` (compliance/fraud) is **never touched** and auto-escalates to a human
- **Audit** — every decision, action, and rupee is written to `audit_log.jsonl`

### Example

> Rahul's ₹999 subscription payment fails with `insufficient_funds`. Instead of retrying today (guaranteed fail), Reclaim schedules a salary-day reminder + retry — and **recovers ₹999**. Had it failed 3 times, the case would escalate to a human queue. Every step is logged.

## 📊 Measured results (batch run, 300 payments)

| Metric | Value |
|---|---|
| Payments at risk | 144 cases |
| Amount at risk | ₹1,37,356 |
| **Money recovered** | **₹92,601** |
| **Recovery rate** | **~67%** |
| Escalated to human queue | 45 (compliance-safe) |

*Honest note: recovery probabilities are modelled estimates calibrated to industry retry-success rates. The agent runs on synthetic data — no live payment data is required or used.*

##  Architecture

```
generate_data.py          agent.py                    report.py / app.py
(synthetic batch)  →  DETECT → DIAGNOSE → ACT   →  measured money recovered
                      (max 3, then ESCALATE)        dashboard + audit viewer
                             ↓
                      audit_log.jsonl  (every decision, timestamped)
```

##  Quick start

```bash
pip install -r requirements.txt

# Terminal metrics
python generate_data.py
python agent.py
python report.py

# Live dashboard (recommended for demos)
streamlit run app.py
```

##  Why this meets the bar

| Requirement | How it's met |
|---|---|
| Measured money recovered across a batch | ₹92,601 recovered across 144 at-risk cases |
| Stopping rules | Hard cap of 3 attempts; no infinite retry loops |
| Compliant escalation | `risk_blocked` never touched; exhausted cases → human queue |
| Audit trail | `audit_log.jsonl` — every action explainable & timestamped |

##  Project structure

```
reclaim/
├── generate_data.py   # synthetic payment batch (~300 records)
├── agent.py           # bounded recovery agent
├── report.py          # money-recovered metrics
├── app.py             # Streamlit dashboard
├── audit_log.jsonl    # audit trail (generated on run)
└── requirements.txt
```

##  Future scope

- Razorpay API integration (live test-mode failed payments)
- Hinglish voice/SMS recovery agent
- Promise-to-pay tracking & B2B receivables chaser

---

Built for Razorpay AI Buildathon 2026 · Track 03 · by Neelapriya K
