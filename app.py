import streamlit as st, pandas as pd, json, subprocess, random
from datetime import datetime

st.set_page_config(page_title="Reclaim — AI Revenue Recovery", page_icon="💸", layout="wide")
st.title("💸 Reclaim — Bounded AI Revenue Recovery Agent")
st.caption("Razorpay AI Buildathon 2026 · Track 03 · Detect → Diagnose → Act → Stop/Escalate")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    n_records = st.slider("Batch size", 100, 1000, 300, 50)
    max_attempts = st.slider("Max recovery attempts (stopping rule)", 1, 5, 3)
    run = st.button("🚀 Generate batch & run agent", type="primary")

def regenerate(n):
    src = open("generate_data.py").read()
    src = src.replace("range(300)", f"range({n})")
    exec(compile(src, "generate_data.py", "exec"), {"__name__": "__main__"})

if run:
    regenerate(n_records)
    agent_src = open("agent.py").read().replace("MAX_ATTEMPTS = 3", f"MAX_ATTEMPTS = {max_attempts}")
    exec(compile(agent_src, "agent.py", "exec"), {"__name__": "__main__"})
    st.success("Agent run complete — audit trail written to audit_log.jsonl")

# Load artifacts if they exist
try:
    results = pd.read_csv("results.csv")
    batch = pd.read_csv("batch.csv")
except FileNotFoundError:
    st.info("👈 Press **Generate batch & run agent** in the sidebar to start.")
    st.stop()

# ---- KPI row ----
at_risk = batch[batch.status == "failed"]
recovered_amt = results["recovered_amount"].sum()
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Amount at risk", f"Rs {at_risk.amount.sum():,.0f}")
c2.metric("✅ Recovered", f"Rs {recovered_amt:,.0f}")
c3.metric("📈 Recovery rate", f"{100*recovered_amt/at_risk.amount.sum():.1f}%")
c4.metric("🙋 Escalated to humans", f"{(results.outcome=='escalated').sum()}")

# ---- Charts ----
left, right = st.columns(2)
by_cause = results.groupby("cause").agg(cases=("txn_id","count"),
                                        recovered=("recovered_amount","sum")).reset_index()
left.subheader("Recovery by failure cause")
left.bar_chart(by_cause.set_index("cause"))
right.subheader("Outcome split")
right.bar_chart(results["outcome"].value_counts())

# ---- Audit trail ----
st.subheader("🧾 Audit trail (every agent decision)")
logs = [json.loads(l) for l in open("audit_log.jsonl")]
log_df = pd.DataFrame(logs)
st.dataframe(log_df.tail(50), use_container_width=True)

# ---- Escalation queue ----
st.subheader("🙋 Human escalation queue")
esc = results[results.outcome == "escalated"]
st.dataframe(esc, use_container_width=True)

st.download_button("⬇️ Download audit log (JSONL)",
                   data=open("audit_log.jsonl").read(),
                   file_name="audit_log.jsonl")
