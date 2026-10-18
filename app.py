"""Teach the Brain once — the same loop as run.py, as a web page.

  doppler run -- .venv/bin/streamlit run app.py            # live model
  LLM_FAKE=1 doppler run -- .venv/bin/streamlit run app.py # offline (stage backup)

Four steps, top to bottom: a guest asks → she teaches the Brain → the agent proposes,
she confirms → every assistant rehearses (laptop now; --boxes = Daytona this afternoon).
"""
import json, os, subprocess, sys, time
import streamlit as st
import assistant, check, correct

st.set_page_config(page_title="Teach the Brain once", layout="wide")
GUESTS = json.load(open("guests.json"))
S = st.session_state

CSS = """
<style>
.stApp { background:#0B0B0C; color:#F4F4F1; }
h1,h2,h3 { color:#F4F4F1 !important; }
.card { background:#1A1A1D; border:1px solid #2C2C30; border-radius:14px; padding:18px 22px; margin:8px 0; }
.card.gold { border-color:#D4AF6D; }
.who { color:#A8A8A3; font-size:0.85rem; letter-spacing:.06em; text-transform:uppercase; }
.pass { color:#34C07C; font-weight:600; } .fail { color:#E25555; font-weight:600; } .dim { color:#A8A8A3; }
.big { font-size:1.35rem; }
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

def card(body, who=None, gold=False):
    w = f'<div class="who">{who}</div>' if who else ""
    st.markdown(f'<div class="card{" gold" if gold else ""}">{w}<div class="big">{body}</div></div>', unsafe_allow_html=True)

def world_start():
    if os.path.exists("ledger.jsonl"): os.remove("ledger.jsonl")
    p = subprocess.Popen([sys.executable, "world/services.py"]); time.sleep(0.5); return p

def rehearse(brain, version):
    world = world_start()
    try:
        out = {}
        for g in GUESTS:
            text = g.get("message") or "EVENT (no guest message): " + json.dumps(g["event"])
            r = assistant.handle(brain, g["id"], text, fake_key=f"{version}:{g['id']}", who=(g["assistant"], g["role"]))
            out[g["id"]] = (check.check(g, r), r)
        return out
    finally:
        world.terminate()

def load_brain(): return json.load(open("brain.json"))

# ---------- header ----------
st.title("Teach the Brain once")
st.caption("One Brain agent · six assistants · rehearsed in sealed sandboxes before going live · fake studio, nothing is sent")

S.setdefault("step", 1)

# ---------- 1. a guest asks ----------
st.header("1 · A guest asks")
g2 = next(x for x in GUESTS if x["id"] == "g2")
if "first_reply" not in S:
    world = world_start()
    try:
        S.first_reply = assistant.handle(load_brain(), g2["id"], g2["message"], fake_key="v0:g2", who=(g2["assistant"], g2["role"]))["reply"]
    finally:
        world.terminate()
card(g2["message"], who="guest · 11:42 pm")
card(S.first_reply, who="On-Brand Support · reads the Brain")

# ---------- 2. she teaches the Brain ----------
st.header("2 · She teaches the Brain agent")
feedback = st.text_input("Not how you'd say it? Tell the Brain agent, in your words.",
                         value="No. 30% deposit at booking, or the spot isn't held.", key="feedback")
if st.button("Teach", type="primary") and feedback.strip():
    S.proposal = correct.propose(load_brain(), feedback, fake_key="round1")
    S.before = None; S.after = None; S.step = 3

# ---------- 3. the agent proposes, she confirms ----------
if S.get("proposal"):
    st.header("3 · The agent proposes · nothing saves until you confirm")
    p = S.proposal
    card(p["summary"], who="Brain agent", gold=True)
    for c in p["changes"]:
        st.markdown(f'<div class="card"><div class="who">{c["path"]}</div>{c["new"]}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5])
    if col1.button("Confirm and save") and not S.get("saved"):
        brain = load_brain()
        S.before = rehearse(brain, "v0")
        brain = correct.apply(brain, p["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
        correct.remember(S.feedback, p); S.saved = True
    if S.get("saved"):
        col2.markdown(f'<span class="pass">Saved to the Brain.</span> <span class="dim">Correction memory holds {len(correct.recall())} learned correction(s).</span>', unsafe_allow_html=True)

# ---------- 4. rehearsal ----------
if S.get("saved"):
    st.header("4 · Rehearsal before going live")
    st.caption("Every assistant that reads the Brain runs its scenario. Plain code marks each reply and each action. No AI marks itself.")
    if st.button("Rehearse every assistant", type="primary") or S.get("after"):
        if not S.get("after"):
            with st.spinner("seven assistants rehearsing…"):
                S.after = rehearse(load_brain(), "v1")
        rows = []
        for g in GUESTS:
            (okb, _), _ = S.before[g["id"]]; (oka, why), r = S.after[g["id"]]
            rows.append({"assistant": g["assistant"], "scenario": g.get("message") or g["label"],
                         "before": "✓" if okb else "✗", "after": "✓" if oka else "✗", "why": "" if oka else why})
        st.table(rows)
        passed = sum(1 for g in GUESTS if S.after[g["id"]][0][0])
        if passed == len(GUESTS):
            st.success("Every assistant is ready. She taught the Brain once. Every assistant followed, proven before going live. Nothing was sent to anyone.")
        else:
            st.error(f"Not ready: {len(GUESTS) - passed} still wrong. Support stays off until every assistant passes.")
        with st.expander("What each assistant said and did"):
            for g in GUESTS:
                _, r = S.after[g["id"]]
                st.markdown(f"**{g['assistant']}** — {r['reply']}")
                for a in r["actions"]:
                    st.code(json.dumps(a), language="json")

st.divider()
if st.button("Reset demo"):
    subprocess.run(["./reset.sh"]); S.clear(); st.rerun()
