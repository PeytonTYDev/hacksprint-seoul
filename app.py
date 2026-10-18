"""Teach the Brain once — the same loop as run.py, as a web page.

  doppler run -- .venv/bin/streamlit run app.py            # live model
  LLM_FAKE=1 doppler run -- .venv/bin/streamlit run app.py # offline (stage backup)

Four steps, top to bottom: a guest asks → she teaches the Brain → the agent proposes,
she confirms → every assistant rehearses (laptop now; --boxes = Daytona this afternoon).
"""
import json, os, subprocess, sys, time
import streamlit as st
import assistant, check, agent

st.set_page_config(page_title="Teach the Brain once", layout="wide")
GUESTS = json.load(open("guests.json"))
S = st.session_state

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"] { background:#000; color:#F4F4F1; font-family:'Geist', -apple-system, system-ui, sans-serif; }
h1, h2, h3 { color:#F4F4F1 !important; font-family:'Geist', system-ui, sans-serif; font-weight:600; letter-spacing:-0.01em; }
h1 { font-size:2rem; } h2 { font-size:1.15rem; margin-top:1.6rem; }
[data-testid="stCaptionContainer"], .dim { color:rgba(255,255,255,0.55); }
.card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10); border-radius:0.75rem; padding:16px 20px; margin:8px 0; }
.card.you { border-left:2px solid #F4F4F1; }
.card.double { border-style:dashed; border-color:rgba(255,255,255,0.30); }
.card.needs-you { border-color:#D4AF6D; }
.who { color:rgba(255,255,255,0.55); font-size:0.78rem; letter-spacing:.06em; text-transform:uppercase; margin-bottom:6px; font-family:'Geist Mono', monospace; }
.big { font-size:1.1rem; line-height:1.5; }
.path { font-family:'Geist Mono', monospace; font-size:0.8rem; color:rgba(255,255,255,0.55); }
.pass { color:#34C07C; font-weight:600; } .fail { color:#E25555; font-weight:600; }
.ready { background:rgba(52,192,124,0.08); border:1px solid #34C07C; border-radius:0.75rem; padding:16px 20px; font-size:1.1rem; }
.notready { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.15); border-radius:0.75rem; padding:16px 20px; font-size:1.1rem; }
.stButton > button { height:36px; padding:0 14px; border-radius:0.75rem; font-family:'Geist', system-ui, sans-serif; font-weight:500; }
.stButton > button[kind="primary"] { background:#F4F4F1; color:#000; border:1px solid #F4F4F1; }
.stButton > button[kind="primary"]:hover { background:#fff; color:#000; }
.stButton > button[kind="secondary"] { background:rgba(255,255,255,0.04); color:#F4F4F1; border:1px solid rgba(255,255,255,0.15); }
.st-key-confirm button, .st-key-confirm2 button { background:transparent !important; color:#D4AF6D !important; border:1px solid #D4AF6D !important; }
[data-testid="stTextInput"] input { background:rgba(255,255,255,0.04); color:#F4F4F1; border:1px solid rgba(255,255,255,0.15); border-radius:0.75rem; font-family:'Geist', system-ui, sans-serif; }
[data-testid="stTable"] table { color:#F4F4F1; border-color:rgba(255,255,255,0.10); font-family:'Geist', system-ui, sans-serif; }
[data-testid="stTable"] th { color:rgba(255,255,255,0.55); font-weight:500; text-transform:lowercase; }
hr { border-color:rgba(255,255,255,0.10); }
.score { width:100%; border-collapse:collapse; margin:8px 0 12px; font-size:0.95rem; }
.score th { text-align:left; color:rgba(255,255,255,0.55); font-weight:500; padding:8px 10px; border-bottom:1px solid rgba(255,255,255,0.15); }
.score td { padding:10px; border-bottom:1px solid rgba(255,255,255,0.08); vertical-align:top; }
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

def card(body, who=None, kind=""):
    """kind: 'you' (founder, solid edge) · 'double' (assistant, dotted edge) · 'needs-you' (lantern, one per view)"""
    w = f'<div class="who">{who}</div>' if who else ""
    st.markdown(f'<div class="card {kind}">{w}<div class="big">{body}</div></div>', unsafe_allow_html=True)

def world_start():
    if os.path.exists("ledger.jsonl"): os.remove("ledger.jsonl")
    p = subprocess.Popen([sys.executable, "world/services.py"]); assistant.wait_for_services(); return p

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
card(g2["message"], who="guest · 11:42 pm", kind="you")
card(S.first_reply, who="On-Brand Support · your double", kind="double")

# ---------- 2. she teaches the Brain ----------
st.header("2 · She teaches the Brain agent")
feedback = st.text_input("Not how you'd say it? Tell the Brain agent, in your words.",
                         value="No. 30% deposit at booking, or the spot isn't held.", key="feedback")
if st.button("Teach", type="primary") and feedback.strip():
    S.proposal = agent.propose(load_brain(), feedback, fake_key="round1")
    S.before = None; S.after = None; S.step = 3

# ---------- 3. the agent proposes, she confirms ----------
if S.get("proposal"):
    st.header("3 · The agent proposes · nothing saves until you confirm")
    p = S.proposal
    card(p["summary"], who="Brain agent · proposed change", kind="needs-you")
    for c in p["changes"]:
        st.markdown(f'<div class="card"><div class="path">{c["path"]}</div><div class="big">{c["new"]}</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5])
    if col1.button("Confirm and save", key="confirm") and not S.get("saved"):
        brain = load_brain()
        S.before = rehearse(brain, "v0")
        brain = agent.apply(brain, p["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
        agent.remember(S.feedback, p); S.saved = True
    if S.get("saved"):
        col2.markdown(f'<span class="pass">Saved to the Brain.</span> <span class="dim">Correction memory holds {len(agent.recall())} learned correction(s).</span>', unsafe_allow_html=True)

# ---------- 4. rehearsal ----------
if S.get("saved"):
    st.header("4 · Rehearsal before going live")
    st.caption("Every assistant that reads the Brain runs its scenario. Plain code marks each reply and each action. No AI marks itself.")
    if st.button("Rehearse every assistant", type="primary") or S.get("after"):
        if not S.get("after"):
            with st.spinner("seven assistants rehearsing…"):
                S.after = rehearse(load_brain(), "v1")
        def did(r):
            """One short line of what the assistant did: actions first, else the reply."""
            acts = []
            for a in r["actions"]:
                t = a["type"]
                if t == "payment_link": acts.append(f"payment link ${a.get('amount')}")
                elif t == "book": acts.append(f"booked {a.get('people')} for {a.get('name')}")
                elif t == "refund": acts.append(f"refund ${a.get('amount')}")
                elif t == "publish_event": acts.append(f"published at ${a.get('price')} · {a.get('deposit_rule','')}")
                elif t == "draft_email": acts.append(f"draft to {a.get('to')}")
                else: acts.append(t.replace("_", " "))
            line = "; ".join(acts) if acts else r["reply"]
            return (line[:110] + "…") if len(line) > 110 else line
        st.markdown('<p class="dim">Before = on the old Brain. After = once she taught it. <span class="fail">wrong</span> = said or did the old thing (quoted $20, kept the unpaid hold). <span class="pass">right</span> = follows the rule she taught. Judged by code against her Brain, not by the AI.</p>', unsafe_allow_html=True)
        html = ['<table class="score"><tr><th>assistant</th><th>scenario</th><th>before</th><th>after</th><th>what it said or did, after</th></tr>']
        for g in GUESTS:
            (okb, _), _ = S.before[g["id"]]; (oka, why), r = S.after[g["id"]]
            b = '<span class="pass">right</span>' if okb else '<span class="fail">wrong</span>'
            a = '<span class="pass">right</span>' if oka else f'<span class="fail">wrong</span> <span class="dim">· {why}</span>'
            html.append(f'<tr><td><b>{g["assistant"]}</b></td><td>{g.get("message") or g["label"]}</td><td>{b}</td><td>{a}</td><td class="dim">{did(r)}</td></tr>')
        html.append("</table>")
        st.markdown("".join(html), unsafe_allow_html=True)
        passed = sum(1 for g in GUESTS if S.after[g["id"]][0][0])
        if passed == len(GUESTS):
            st.markdown('<div class="ready"><span class="pass">Every assistant is ready.</span> She taught the Brain once. Every assistant followed, proven before going live. Nothing was sent to anyone.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="notready"><span class="fail">Not ready.</span> {len(GUESTS) - passed} still wrong. Nothing goes live until every assistant passes.</div>', unsafe_allow_html=True)
            S.setdefault("round", 2)
            if S.round <= 3:
                failures = "; ".join(f"{g['assistant']} ({g['id']}): {S.after[g['id']][0][1]}" for g in GUESTS if not S.after[g["id"]][0][0])
                st.subheader(f"5 · The agent proposes again · round {S.round}")
                if st.button("Ask the agent what else to change"):
                    S.proposal2 = agent.propose(load_brain(), f"Rehearsal failures: {failures}. Original correction: {S.feedback}", fake_key=f"round{S.round}")
                if S.get("proposal2"):
                    p2 = S.proposal2
                    card(p2["summary"], who="Brain agent · proposed change", kind="needs-you")
                    for c in p2["changes"]:
                        st.markdown(f'<div class="card"><div class="path">{c["path"]}</div><div class="big">{c["new"]}</div></div>', unsafe_allow_html=True)
                    if st.button("Confirm and rehearse again", key="confirm2"):
                        brain = agent.apply(load_brain(), p2["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
                        agent.remember(S.feedback, p2)
                        with st.spinner("rehearsing again…"):
                            S.before, S.after = S.after, rehearse(brain, f"v{S.round}")
                        S.round += 1; S.proposal2 = None; st.rerun()
        with st.expander("What each assistant said and did"):
            for g in GUESTS:
                _, r = S.after[g["id"]]
                st.markdown(f"**{g['assistant']}** — {r['reply']}")
                for a in r["actions"]:
                    st.code(json.dumps(a), language="json")

st.divider()
if st.button("Reset demo"):
    subprocess.run(["./reset.sh"]); S.clear(); st.rerun()
