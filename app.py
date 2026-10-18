"""Teach the Brain once — the same loop as run.py, as a web page.

  doppler run -- .venv/bin/streamlit run app.py            # live model
  LLM_FAKE=1 doppler run -- .venv/bin/streamlit run app.py # offline (stage backup)

Four steps, top to bottom: a guest asks → she teaches the Brain → the agent proposes,
she confirms → every assistant rehearses (laptop now; --boxes = Daytona this afternoon).
"""
import json, os, subprocess, sys, time
import streamlit as st
import assistant, check, brain_agent

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
/* ---- MystFlo shell: left rail + masthead, from docs/design/design-artifacts/shell.html ---- */
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#000; border-right:1px solid rgba(255,255,255,0.10); }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top:12px; }
.brand { display:flex; align-items:center; gap:12px; padding:8px 4px 18px; }
.brand-mark { width:24px; height:26px; min-width:24px; display:inline-block; background:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20140%20148%22%20fill%3D%22none%22%20stroke%3D%22%23F4F4F1%22%3E%3Cpath%20d%3D%22M86%2014%20C106%2032%20110%2060%2086%2088%20C62%2060%2066%2032%2086%2014%20Z%22%20stroke-width%3D%224%22%20stroke-dasharray%3D%224%209%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%3Cpath%20d%3D%22M86%2088%20C86%20104%2056%20102%2056%20114%22%20stroke-width%3D%224%22%20stroke-dasharray%3D%224%209%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%3Ccircle%20cx%3D%2286%22%20cy%3D%2288%22%20r%3D%224%22%20stroke-width%3D%223%22%20opacity%3D%22.8%22%2F%3E%3Cpath%20d%3D%22M56%2024%20C76%2042%2080%2070%2056%2098%20C32%2070%2036%2042%2056%2024%20Z%22%20stroke-width%3D%224.5%22%2F%3E%3Cline%20x1%3D%2256%22%20y1%3D%2240%22%20x2%3D%2256%22%20y2%3D%2286%22%20stroke-width%3D%222.5%22%20opacity%3D%22.45%22%2F%3E%3Cline%20x1%3D%2256%22%20y1%3D%2298%22%20x2%3D%2256%22%20y2%3D%22132%22%20stroke-width%3D%224.5%22%2F%3E%3Ccircle%20cx%3D%2256%22%20cy%3D%2298%22%20r%3D%226%22%20fill%3D%22%23F4F4F1%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2256%22%20cy%3D%22114%22%20r%3D%225%22%20stroke-width%3D%223%22%2F%3E%3C%2Fsvg%3E") no-repeat center / contain; }
.wordmark-block { display:flex; flex-direction:column; line-height:1; }
.wordmark { font-family:Georgia,'Times New Roman',serif; font-size:22px; font-weight:400; letter-spacing:-.015em; color:#F4F4F1; text-shadow:0 0 20px rgba(255,255,255,.18); white-space:nowrap; }
.wordmark i { font-style:italic; }
.wordmark-suffix { font-size:9px; letter-spacing:.4em; text-transform:uppercase; color:rgba(255,255,255,0.40); margin-top:5px; margin-left:1px; }
.badge-proto { font-size:9px; letter-spacing:.06em; text-transform:uppercase; font-weight:500; border-radius:999px; padding:2.5px 8px; white-space:nowrap; background:rgba(234,179,8,.15); border:1px solid rgba(234,179,8,.30); color:#eab308; margin-left:auto; }
.rail-eyebrow { font-size:9.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(255,255,255,0.30); padding:12px 12px 6px; }
.nav-item { display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:10px; font-size:13px; font-weight:300; letter-spacing:.01em; color:rgba(255,255,255,0.55); min-height:40px; position:relative; }
.nav-item .ic { width:15px; height:15px; flex-shrink:0; opacity:.8; border:1.2px solid currentColor; border-radius:4px; display:inline-block; }
.nav-item .ic-round { border-radius:50%; }
.nav-item.active-quiet { color:#F4F4F1; background:rgba(255,255,255,0.06); font-weight:400; }
.nav-item.active-quiet::before { content:""; position:absolute; left:-6px; top:8px; bottom:8px; width:2px; border-radius:2px; background:linear-gradient(to bottom, transparent, rgba(255,255,255,.9), transparent); box-shadow:0 0 12px rgba(255,255,255,.35); }
.eyebrow-page { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:rgba(255,255,255,0.40); margin-bottom:10px; font-family:'Geist Mono', monospace; }
h1.page-h1, [data-testid="stMarkdownContainer"] h1.page-h1 { font-size:26px !important; font-weight:300 !important; letter-spacing:-.01em; color:#F4F4F1; margin:0 0 6px !important; padding:0 !important; }
[data-testid="stHeading"] h2, .stMarkdown h2 { font-size:17px !important; font-weight:500 !important; margin-top:1.6rem !important; padding-bottom:0 !important; }
[data-testid="stHeading"] h3, .stMarkdown h3 { font-size:15px !important; font-weight:500 !important; }
.intro { color:rgba(255,255,255,0.55); font-size:13.5px; margin:0 0 8px; }
.panel { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10); border-radius:1rem; padding:16px 20px 4px; margin:8px 0 16px; }
.block-container { padding-top:2.2rem; max-width:1120px; }
[data-testid="stSidebar"] p.proto-foot { color:rgba(255,255,255,0.40) !important; font-size:11.5px !important; line-height:1.5; font-family:'Geist', system-ui, sans-serif; margin-top:24px; }
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
    if S.get("boxes"):
        import box
        log = []
        out = box.rehearse_in_boxes(version, log=log.append)
        S.boxlog = log[-1] if log else ""
        return {sid: (check.check(next(g for g in GUESTS if g["id"] == sid), r), r) for sid, r in out.items()}
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

# ---------- MystFlo shell: left rail (the product's nav, Brain lit) ----------
MARK = '<span class="brand-mark"></span>'   # the Mark, drawn as a background so the markdown sanitizer leaves it alone
def nav(label, active=False, round_=False):
    return f'<div class="nav-item{" active-quiet" if active else ""}"><span class="ic{" ic-round" if round_ else ""}"></span>{label}</div>'

S.setdefault("step", 1)
with st.sidebar:
    st.markdown(f'<div class="brand">{MARK}<span class="wordmark-block"><span class="wordmark"><i>Myst</i>Flo</span>'
                f'<span class="wordmark-suffix">Platform</span></span><span class="badge-proto">Prototype</span></div>'
                + nav("Assistants") + nav("Brain", active=True, round_=True) + nav("Pulse") + nav("Team", round_=True) + nav("Connects")
                + '<div class="rail-eyebrow">Rehearsal</div>', unsafe_allow_html=True)
    S.boxes = st.toggle("Rehearse in Daytona sandboxes", value=S.get("boxes", True), help="Off = run the seven scenarios on this laptop")
    st.caption("One fresh sandbox per assistant, all at once, deleted after. Built at the event.")
    st.markdown('<p class="proto-foot">Prototype built outside MystFlo for Daytona HackSprint Seoul. This is where it would sit in the product. Fake studio, nothing is sent.</p>', unsafe_allow_html=True)

# ---------- header: the Brain page ----------
st.markdown('<div class="eyebrow-page">Brain · your double learns from you</div>'
            '<h1 class="page-h1">Teach the Brain once</h1>'
            '<p class="intro">One Brain agent · six assistants read the same Brain · rehearsed in sealed sandboxes before going live</p>', unsafe_allow_html=True)

# ---------- 1. a guest asks ----------
st.header("1 · A guest asks, your double answers")
g2 = next(x for x in GUESTS if x["id"] == "g2")
if "first_reply" not in S:
    world = world_start()
    try:
        S.first_reply = assistant.handle(load_brain(), g2["id"], g2["message"], fake_key="v0:g2", who=(g2["assistant"], g2["role"]))["reply"]
    finally:
        world.terminate()
card(g2["message"], who="guest on WhatsApp · 11:42 pm · from Pulse", kind="you")
card(S.first_reply, who="On-Brand Support · your double · what it answered", kind="double")

# ---------- 2. she teaches the Brain ----------
st.header("2 · You teach your Brain")
feedback = st.text_input("Not how you'd say it? Tell the Brain agent, in your words.",
                         value="No. 30% deposit at booking, or the spot isn't held.", key="feedback")
if st.button("Teach", type="primary") and feedback.strip():
    S.proposal = brain_agent.propose(load_brain(), feedback, fake_key="round1")
    S.before = None; S.after = None; S.step = 3

# ---------- 3. the agent proposes, she confirms ----------
if S.get("proposal"):
    st.header("3 · Your Brain proposes · nothing saves until you confirm")
    p = S.proposal
    card(p["summary"], who="Your Brain · proposed change · needs you", kind="needs-you")
    for c in p["changes"]:
        st.markdown(f'<div class="card"><div class="path">{c["path"]}</div><div class="big">{c["new"]}</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5])
    if col1.button("Confirm and save", key="confirm") and not S.get("saved"):
        brain = load_brain()
        S.before = rehearse(brain, "v0")
        brain = brain_agent.apply(brain, p["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
        brain_agent.remember(S.feedback, p); S.saved = True
    if S.get("saved"):
        col2.markdown(f'<span class="pass">Saved to the Brain.</span> <span class="dim">Correction memory holds {len(brain_agent.recall())} learned correction(s).</span>', unsafe_allow_html=True)

# ---------- 4. rehearsal ----------
if S.get("saved"):
    st.header("4 · Rehearsal before going live")
    st.markdown('<div class="eyebrow-page">Pulse · rehearsal · every assistant that reads this Brain</div>', unsafe_allow_html=True)
    st.caption("Every assistant that reads the Brain runs its scenario. Plain code marks each reply and each action. No AI marks itself.")
    if st.button("Rehearse every assistant", type="primary") or S.get("after"):
        if not S.get("after"):
            with st.spinner("seven assistants rehearsing" + (" in seven sandboxes…" if S.get("boxes") else "…")):
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
        boxcol = "<th>sandbox</th>" if S.get("boxes") else ""
        html = [f'<table class="score"><tr><th>assistant</th><th>scenario</th><th>before</th><th>after</th><th>what it said or did, after</th>{boxcol}</tr>']
        for g in GUESTS:
            (okb, _), _ = S.before[g["id"]]; (oka, why), r = S.after[g["id"]]
            b = '<span class="pass">right</span>' if okb else '<span class="fail">wrong</span>'
            a = '<span class="pass">right</span>' if oka else f'<span class="fail">wrong</span> <span class="dim">· {why}</span>'
            bx = f'<td class="dim">{r.get("box", "-")} · {r.get("seconds", "")}s</td>' if S.get("boxes") else ""
            html.append(f'<tr><td><b>{g["assistant"]}</b></td><td>{g.get("message") or g["label"]}</td><td>{b}</td><td>{a}</td><td class="dim">{did(r)}</td>{bx}</tr>')
        html.append("</table>")
        st.markdown("".join(html), unsafe_allow_html=True)
        if S.get("boxes") and S.get("boxlog"):
            st.markdown(f'<p class="dim">Daytona: {S.boxlog}</p>', unsafe_allow_html=True)
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
                    S.proposal2 = brain_agent.propose(load_brain(), f"Rehearsal failures: {failures}. Original correction: {S.feedback}", fake_key=f"round{S.round}")
                if S.get("proposal2"):
                    p2 = S.proposal2
                    card(p2["summary"], who="Your Brain · proposed change · needs you", kind="needs-you")
                    for c in p2["changes"]:
                        st.markdown(f'<div class="card"><div class="path">{c["path"]}</div><div class="big">{c["new"]}</div></div>', unsafe_allow_html=True)
                    if st.button("Confirm and rehearse again", key="confirm2"):
                        brain = brain_agent.apply(load_brain(), p2["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
                        brain_agent.remember(S.feedback, p2)
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
