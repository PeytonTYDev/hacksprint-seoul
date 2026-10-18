"""Teach the Brain once — the same loop as run.py, drawn as the product's Brain page (the Brain agent design:
the page as a conversation, You solid / Your Brain dotted, one composer, a right column in counts).

  doppler run -- .venv/bin/streamlit run app.py            # live model
  LLM_FAKE=1 doppler run -- .venv/bin/streamlit run app.py # offline (stage backup)

The thread: your double answered a guest → you teach your Brain in the composer → your Brain proposes,
you confirm → every assistant rehearses (Daytona sandboxes when the rail toggle is on).
"""
import json, os, subprocess, sys, time
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st
import assistant, check, brain_agent

st.set_page_config(page_title="Brain · Teach the Brain once", layout="wide", initial_sidebar_state="expanded")
GUESTS = json.load(open("guests.json"))
S = st.session_state
_host = urlparse(os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")).hostname or ""
ENGINE = ("Nosana GPU" if "nosana" in _host else _host) + " · " + os.getenv("LLM_MODEL", "google/gemini-3.1-flash-lite")
def now(): return datetime.now().strftime("%-H:%M")

MARK_CSS = '.brand-mark { width:24px; height:26px; min-width:24px; display:inline-block; background:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20140%20148%22%20fill%3D%22none%22%20stroke%3D%22%23F4F4F1%22%3E%3Cpath%20d%3D%22M86%2014%20C106%2032%20110%2060%2086%2088%20C62%2060%2066%2032%2086%2014%20Z%22%20stroke-width%3D%224%22%20stroke-dasharray%3D%224%209%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%3Cpath%20d%3D%22M86%2088%20C86%20104%2056%20102%2056%20114%22%20stroke-width%3D%224%22%20stroke-dasharray%3D%224%209%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%3Ccircle%20cx%3D%2286%22%20cy%3D%2288%22%20r%3D%224%22%20stroke-width%3D%223%22%20opacity%3D%22.8%22%2F%3E%3Cpath%20d%3D%22M56%2024%20C76%2042%2080%2070%2056%2098%20C32%2070%2036%2042%2056%2024%20Z%22%20stroke-width%3D%224.5%22%2F%3E%3Cline%20x1%3D%2256%22%20y1%3D%2240%22%20x2%3D%2256%22%20y2%3D%2286%22%20stroke-width%3D%222.5%22%20opacity%3D%22.45%22%2F%3E%3Cline%20x1%3D%2256%22%20y1%3D%2298%22%20x2%3D%2256%22%20y2%3D%22132%22%20stroke-width%3D%224.5%22%2F%3E%3Ccircle%20cx%3D%2256%22%20cy%3D%2298%22%20r%3D%226%22%20fill%3D%22%23F4F4F1%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2256%22%20cy%3D%22114%22%20r%3D%225%22%20stroke-width%3D%223%22%2F%3E%3C%2Fsvg%3E") no-repeat center / contain; }'
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"] { background:#000; color:#F4F4F1; font-family:'Geist', -apple-system, system-ui, sans-serif; }
header[data-testid="stHeader"] { display:none; }
.block-container { padding-top:84px; padding-bottom:3rem; max-width:1320px; }
[data-testid="stSidebar"] { background:#0a0a0a; border-right:1px solid rgba(255,255,255,0.10); top:64px; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top:0; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top:14px; }
[data-testid="stSidebarCollapseButton"] { display:none; }
/* ---- masthead, from docs/design/design-artifacts/shell.html ---- */
.mf-top { position:fixed; top:0; left:0; right:0; height:64px; z-index:1000; background:#000; border-bottom:1px solid rgba(255,255,255,0.10);
          display:flex; align-items:center; gap:14px; padding:0 24px; }
.brand { display:flex; align-items:center; gap:12px; }
MARKCSS
.wordmark-block { display:flex; flex-direction:column; line-height:1; }
.wordmark { font-family:Georgia,'Times New Roman',serif; font-size:22px; font-weight:400; letter-spacing:-.015em; color:#F4F4F1; text-shadow:0 0 20px rgba(255,255,255,.18); white-space:nowrap; }
.wordmark i { font-style:italic; }
.wordmark-suffix { font-size:9px; letter-spacing:.4em; text-transform:uppercase; color:rgba(255,255,255,0.40); margin-top:5px; margin-left:1px; }
.badge-proto { font-size:9px; letter-spacing:.06em; text-transform:uppercase; font-weight:500; border-radius:999px; padding:2.5px 8px; white-space:nowrap; background:rgba(234,179,8,.15); border:1px solid rgba(234,179,8,.30); color:#eab308; margin-left:10px; }
.top-links { color:rgba(255,255,255,0.55); font-size:13.5px; font-weight:300; margin-left:6px; }
.top-progress { margin:0 auto; text-align:center; font-size:13px; color:#F4F4F1; font-weight:300; }
.top-progress .n { font-family:'Geist Mono', monospace; font-size:11px; letter-spacing:.14em; color:rgba(255,255,255,0.55); margin-right:10px; }
.top-progress .bar { height:1px; background:rgba(255,255,255,0.15); margin-top:8px; position:relative; }
.top-progress .bar i { position:absolute; left:0; top:0; height:1px; background:#F4F4F1; }
.top-right { color:rgba(255,255,255,0.55); font-size:13.5px; font-weight:300; white-space:nowrap; }
.top-right b { color:#F4F4F1; font-weight:400; }
/* ---- rail ---- */
.rail-eyebrow { font-size:9.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(255,255,255,0.30); padding:12px 12px 6px; }
.nav-item { display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:10px; font-size:13px; font-weight:300; letter-spacing:.01em; color:rgba(255,255,255,0.55); min-height:40px; position:relative; }
.nav-item .ic { width:15px; height:15px; flex-shrink:0; opacity:.8; border:1.2px solid currentColor; border-radius:4px; display:inline-block; }
.nav-item .ic-round { border-radius:50%; }
.nav-item.active-quiet { color:#F4F4F1; background:rgba(255,255,255,0.06); font-weight:400; }
.nav-item.active-quiet::before { content:""; position:absolute; left:-6px; top:8px; bottom:8px; width:2px; border-radius:2px; background:linear-gradient(to bottom, transparent, rgba(255,255,255,.9), transparent); box-shadow:0 0 12px rgba(255,255,255,.35); }
[data-testid="stSidebar"] p.proto-foot { color:rgba(255,255,255,0.40) !important; font-size:11.5px !important; line-height:1.5; margin-top:24px; }
/* ---- page head ---- */
h1.page-h1, [data-testid="stMarkdownContainer"] h1.page-h1 { font-size:26px !important; font-weight:300 !important; letter-spacing:-.01em; color:#F4F4F1; margin:0 0 6px !important; padding:0 !important; }
.intro { color:rgba(255,255,255,0.55); font-size:13.5px; margin:0 0 18px; }
/* ---- pinned building line ---- */
.pinned { border:1px solid rgba(255,255,255,0.10); border-radius:12px; padding:12px 16px; margin:0 0 18px; background:rgba(255,255,255,0.03); }
.pinned .lab { font-size:9.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(255,255,255,0.40); display:flex; justify-content:space-between; }
.pinned .lab b { color:#F4F4F1; font-weight:400; letter-spacing:0; text-transform:none; font-size:12px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
.chip { font-size:11.5px; color:rgba(255,255,255,0.55); border:1px solid rgba(255,255,255,0.12); border-radius:999px; padding:3px 10px; }
.chip.on { color:#F4F4F1; border-color:rgba(255,255,255,0.30); }
.chip.gold { color:#D4AF6D; border-color:rgba(212,175,109,0.55); }
/* ---- thread ---- */
.meta { font-size:11px; color:rgba(255,255,255,0.40); margin:0 0 4px; font-family:'Geist Mono', monospace; }
[class*="st-key-turn-brain"] { border-left:1.5px dashed rgba(255,255,255,0.35); padding:4px 0 6px 16px; margin:14px 0; }
[class*="st-key-turn-brain"] .meta::before { content:"◌ "; }
[class*="st-key-turn-you"] { width:72% !important; margin:14px 0 14px auto !important; border-right:2px solid #F4F4F1; padding:4px 16px 6px 0; }
[class*="st-key-turn-you"] .meta { text-align:right; }
[class*="st-key-turn-you"] .meta::after { content:" ●"; }
.big { font-size:1.02rem; line-height:1.5; }
.quote { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10); border-radius:10px; padding:10px 14px; margin:8px 0; }
.quote .who { font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; color:rgba(255,255,255,0.45); margin-bottom:4px; font-family:'Geist Mono', monospace; }
.quote.double { border-style:dashed; }
.ready-box { border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:12px 14px; margin:8px 0; }
.ready-box .head { display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px; }
.ready-box .head span:last-child { color:rgba(255,255,255,0.45); }
.change { display:grid; grid-template-columns:150px 1fr; gap:12px; padding:8px 0; border-top:1px solid rgba(255,255,255,0.08); font-size:13.5px; }
.change .path { font-family:'Geist Mono', monospace; font-size:11.5px; color:rgba(255,255,255,0.55); }
.note { font-size:12.5px; color:rgba(255,255,255,0.45); }
.pass { color:#34C07C; font-weight:600; } .fail { color:#E25555; font-weight:600; }
.ready { background:rgba(52,192,124,0.08); border:1px solid #34C07C; border-radius:0.75rem; padding:12px 16px; font-size:1rem; margin:8px 0; }
.notready { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.15); border-radius:0.75rem; padding:12px 16px; font-size:1rem; margin:8px 0; }
.dim { color:rgba(255,255,255,0.55); }
.eyebrow-page { font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color:rgba(255,255,255,0.40); margin:4px 0 8px; font-family:'Geist Mono', monospace; }
.score { width:100%; border-collapse:collapse; margin:6px 0 10px; font-size:0.86rem; }
.score th { text-align:left; color:rgba(255,255,255,0.55); font-weight:500; padding:6px 8px; border-bottom:1px solid rgba(255,255,255,0.15); }
.score td { padding:8px; border-bottom:1px solid rgba(255,255,255,0.08); vertical-align:top; }
/* ---- right column ---- */
.rc-eyebrow { font-size:9.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(255,255,255,0.40); display:flex; align-items:center; gap:10px; margin:18px 0 10px; }
.rc-eyebrow::after { content:""; flex:1; height:1px; background:rgba(255,255,255,0.10); }
.rc-stand { font-size:30px; font-weight:300; color:#F4F4F1; line-height:1; }
.rc-stand small { font-size:12px; color:rgba(255,255,255,0.45); margin-left:8px; }
.rc-sub { font-size:12.5px; color:rgba(255,255,255,0.45); margin-top:8px; }
.rc-next { border:1px solid rgba(212,175,109,0.55); background:rgba(212,175,109,0.08); border-radius:10px; padding:10px 12px; color:#D4AF6D; font-size:13.5px; }
.rc-next small { display:block; color:rgba(212,175,109,0.75); font-size:11.5px; margin-top:3px; }
.rc-row { display:flex; justify-content:space-between; gap:12px; font-size:12.5px; padding:7px 0; border-bottom:1px solid rgba(255,255,255,0.08); color:rgba(255,255,255,0.75); }
.rc-row span:last-child { color:rgba(255,255,255,0.40); font-family:'Geist Mono', monospace; font-size:11px; white-space:nowrap; flex-shrink:0; }
.rc-row b { font-family:'Geist Mono', monospace; font-weight:400; font-size:11px; color:rgba(255,255,255,0.55); margin-right:8px; }
/* ---- widgets ---- */
.stButton > button { height:36px; padding:0 14px; border-radius:999px; font-family:'Geist', system-ui, sans-serif; font-weight:500; }
.stButton > button[kind="primary"] { background:#F4F4F1; color:#000; border:1px solid #F4F4F1; }
.stButton > button[kind="secondary"] { background:rgba(255,255,255,0.04); color:#F4F4F1; border:1px solid rgba(255,255,255,0.15); }
.st-key-confirm button, .st-key-confirm2 button { background:transparent !important; color:#D4AF6D !important; border:1px solid #D4AF6D !important; }
[data-testid="stTextInput"] input { background:rgba(255,255,255,0.03); color:#F4F4F1; border:1px solid rgba(255,255,255,0.15); border-radius:14px; height:48px; font-family:'Geist', system-ui, sans-serif; }
[data-testid="stTextInput"] label { color:rgba(255,255,255,0.45) !important; font-size:12px !important; }
hr { border-color:rgba(255,255,255,0.10); }
</style>"""
st.markdown(CSS.replace("MARKCSS", MARK_CSS), unsafe_allow_html=True)

# ---------- helpers ----------
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
def md(html): st.markdown(html, unsafe_allow_html=True)
class turn:
    """A thread row as a keyed container: Your Brain = dotted left rule, You = solid right rule (the Double Law)."""
    _n = 0
    def __init__(self, who, t):
        turn._n += 1
        kind = "you" if who == "You" else "brain"
        self.c = st.container(key=f"turn-{kind}-{turn._n}")
        self.who, self.t = who, t
    def __enter__(self):
        self.c.__enter__(); md(f'<div class="meta">{self.who} · {self.t}</div>'); return self
    def __exit__(self, *a): return self.c.__exit__(*a)
def changes_html(p):
    rows = "".join(f'<div class="change"><span class="path">{c["path"]}</span><span>{c["new"]}</span></div>' for c in p["changes"])
    return f'<div class="ready-box"><div class="head"><span>● Ready to confirm · {len(p["changes"])}</span><span>deposit · {p["summary"][:60]}</span></div>{rows}</div>'
def did(r):
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
    return (line[:100] + "…") if len(line) > 100 else line

S.setdefault("log", [])            # activity, newest first: (text, time)
def logit(text): S.log.insert(0, (text, now()))

# ---------- masthead (the product's, with a Prototype badge instead of Private beta) ----------
all_right = bool(S.get("after")) and all(S.after[g["id"]][0][0] for g in GUESTS)
stage = 1 if not S.get("proposal") else 2 if not S.get("saved") else 3 if not S.get("after") else 4
stage_text = {1: "Teach your Brain", 2: "Confirm the change", 3: "Rehearse every assistant", 4: "Ready to go live" if all_right else "A miss · your Brain proposes again"}[stage]
md(f'<div class="mf-top"><div class="brand"><span class="brand-mark"></span><span class="wordmark-block"><span class="wordmark"><i>Myst</i>Flo</span>'
   f'<span class="wordmark-suffix">Platform</span></span></div><span class="badge-proto">Prototype</span>'
   f'<span class="top-links">Feedback · Let MystFlo help setup</span>'
   f'<div class="top-progress"><span class="n">{stage} OF 4</span>{stage_text}<div class="bar" style="width:260px"><i style="width:{stage*25}%"></i></div></div>'
   f'<span class="top-right"><b>Mud &amp; Fire Pottery</b> · fake studio · nothing is sent</span></div>')

# ---------- rail ----------
def nav(label, active=False, round_=False):
    return f'<div class="nav-item{" active-quiet" if active else ""}"><span class="ic{" ic-round" if round_ else ""}"></span>{label}</div>'
with st.sidebar:
    md('<div class="rail-eyebrow">Workspace</div>' + nav("Assistants") + nav("Brain", active=True, round_=True) + nav("Pulse") + nav("Team", round_=True) + nav("Connects")
       + '<div class="rail-eyebrow">Rehearsal</div>')
    S.boxes = st.toggle("Rehearse in Daytona sandboxes", value=S.get("boxes", True), help="Off = run the seven scenarios on this laptop")
    st.caption("One fresh sandbox per assistant, all at once, deleted after.")
    md('<div class="rail-eyebrow">Engine</div><p class="proto-foot" style="margin-top:0">' + ENGINE + ' · swap with LLM_BASE_URL / LLM_MODEL</p>')
    md('<p class="proto-foot">Prototype for Daytona HackSprint Seoul, drawn as the product\'s Brain page. Fake studio, nothing is sent.</p>')

left, right = st.columns([2.35, 1], gap="large")

# =================== main column: the Brain page as a conversation ===================
with left:
    md('<h1 class="page-h1">Brain</h1><p class="intro">The Brain holds how you run your business — every assistant reads it.</p>')
    state = "every assistant ready" if all_right else "waiting on you ↓"
    chips = [("Support flagged a reply", True), ("You taught", stage >= 2), ("Confirmed · v2", stage >= 3), ("Rehearsed · 7 assistants", stage >= 4)]
    md('<div class="pinned"><div class="lab"><span>Building your Brain</span><b>● ' + state + '</b></div><div class="chips">'
       + "".join(f'<span class="chip{" on" if on else ""}">{t}</span>' for t, on in chips) + '</div></div>')

    # turn 1 · Your Brain brings what the double answered
    g2 = next(x for x in GUESTS if x["id"] == "g2")
    if "first_reply" not in S:
        world = world_start()
        try:
            S.first_reply = assistant.handle(load_brain(), g2["id"], g2["message"], fake_key="v0:g2", who=(g2["assistant"], g2["role"]))["reply"]
        finally:
            world.terminate()
        S.t0 = now(); logit("On-Brand Support answered a guest · flagged for you")
    with turn("Your Brain", S.t0):
      md('<div class="big">On-Brand Support answered a guest last night. Is this how you\'d say it?</div>'
       f'<div class="quote"><div class="who">guest on WhatsApp · 11:42 pm</div>{g2["message"]}</div>'
       f'<div class="quote double"><div class="who">On-Brand Support · your double</div>{S.first_reply}</div>'
       '<p class="note">Not how you\'d say it? Tell your Brain below, in your words.</p>')

    # composer (until taught)
    if not S.get("proposal"):
        feedback = st.text_input("Tell your Brain anything — a rule, a price, how you\'d say it. Try the full rule, or just \"Deposit is 30%.\" and watch the rehearsal catch what you left out",
                                 value="No. 30% deposit at booking, or the spot isn't held.", key="feedback")
        if st.button("Teach", type="primary") and feedback.strip():
            S.taught = feedback.strip(); S.t1 = now()
            S.proposal = brain_agent.propose(load_brain(), feedback, fake_key="round1"); S.t2 = now()
            S.before = None; S.after = None
            logit("You taught: " + S.taught[:48]); logit(f"Your Brain proposed {len(S.proposal['changes'])} changes")
            st.rerun()

    # turn 2 · You taught
    if S.get("proposal"):
        with turn("You", S.t1): md(f'<div class="big">{S.taught}</div>')

        # turn 3 · Your Brain proposes, you confirm
        p = S.proposal
        with turn("Your Brain", S.t2):
            md(f'<div class="big">{p["summary"]}</div>' + changes_html(p))
            if not S.get("saved"):
                c1, c2 = st.columns([1, 2.2])
                if c1.button("Confirm and save", key="confirm"):
                    brain = load_brain()
                    where = " in seven Daytona sandboxes" if S.get("boxes") else ""
                    with st.spinner("recording how every assistant behaves on the old Brain" + where + "…"):
                        S.before = rehearse(brain, "v0")
                    brain = brain_agent.apply(brain, p["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
                    brain_agent.remember(S.taught, p)
                    S.saved = True; S.t3 = now()
                    logit("Confirmed · saved as v2 · 1 correction remembered")
                    with st.spinner("saved · now every assistant rehearses on v2" + where + "…"):
                        S.after = rehearse(brain, "v1")
                    S.t4 = now(); logit("Rehearsed 7 assistants" + (" · 7 sandboxes" if S.get("boxes") else "")); st.rerun()
                c2.markdown('<p class="note" style="margin-top:8px">Nothing is saved until you confirm.</p>', unsafe_allow_html=True)
            else:
                md(f'<p class="note"><span class="pass">Saved as v2.</span> Correction memory holds {len(brain_agent.recall())} learned correction(s).</p>')

    # turn 4 · rehearsal before going live
    if S.get("saved"):
        with turn("Your Brain", S.t3):
            md('<div class="big">Saved. Before it goes live, every assistant that reads this Brain rehearses its scenario'
               + (' in its own Daytona sandbox' if S.get("boxes") else ' on this laptop') + '. Plain code marks each reply and each action. No AI marks itself.</div>')
            if not S.get("after"):
                if st.button("Rehearse every assistant", type="primary"):
                    with st.spinner("seven assistants rehearsing" + (" in seven sandboxes…" if S.get("boxes") else "…")):
                        S.after = rehearse(load_brain(), "v1")
                    S.t4 = now(); logit("Rehearsed 7 assistants" + (" · 7 sandboxes" if S.get("boxes") else "")); st.rerun()
            if S.get("after"):
                md(f'<div class="eyebrow-page">Pulse · rehearsal · before = old Brain · after = v2 · engine {ENGINE}</div>')
                boxcol = "<th>sandbox</th>" if S.get("boxes") else ""
                html = [f'<table class="score"><tr><th>assistant</th><th>scenario</th><th>before</th><th>after</th><th>what it said or did, after</th>{boxcol}</tr>']
                for g in GUESTS:
                    (okb, _), _ = S.before[g["id"]]; (oka, why), r = S.after[g["id"]]
                    b = '<span class="pass">right</span>' if okb else '<span class="fail">wrong</span>'
                    a = '<span class="pass">right</span>' if oka else f'<span class="fail">wrong</span> <span class="dim">· {why}</span>'
                    bx = f'<td class="dim">{r.get("box", "-")} · {r.get("seconds", "")}s</td>' if S.get("boxes") else ""
                    html.append(f'<tr><td><b>{g["assistant"]}</b></td><td>{g.get("message") or g["label"]}</td><td>{b}</td><td>{a}</td><td class="dim">{did(r)}</td>{bx}</tr>')
                html.append("</table>")
                md("".join(html))
                md('<p class="note"><span class="fail">wrong</span> = said or did the old thing (quoted $20, kept the unpaid hold). <span class="pass">right</span> = follows the rule you taught. Judged by code against your Brain.'
                   + (f' · Daytona: {S.boxlog}' if S.get("boxes") and S.get("boxlog") else '') + '</p>')
                passed = sum(1 for g in GUESTS if S.after[g["id"]][0][0])
                if passed == len(GUESTS):
                    md('<div class="ready"><span class="pass">Every assistant is ready.</span> You taught the Brain once. Every assistant followed, proven before going live. Nothing was sent to anyone.</div>')
                else:
                    md(f'<div class="notready"><span class="fail">Not ready.</span> {len(GUESTS) - passed} still wrong. Nothing goes live until every assistant passes.</div>')
                    S.setdefault("round", 2)
                    if S.round <= 3:
                        failures = "; ".join(f"{g['assistant']} ({g['id']}): {S.after[g['id']][0][1]}" for g in GUESTS if not S.after[g["id"]][0][0])
                        if st.button("Fix it · ask your Brain", type="primary"):
                            S.proposal2 = brain_agent.propose(load_brain(), f"Rehearsal failures: {failures}. Original correction: {S.taught}", fake_key=f"round{S.round}")
                        if S.get("proposal2"):
                            p2 = S.proposal2
                            md(f'<div class="big">{p2["summary"]}</div>' + changes_html(p2))
                            if st.button("Confirm and rehearse again", key="confirm2"):
                                brain = brain_agent.apply(load_brain(), p2["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
                                brain_agent.remember(S.taught, p2); logit(f"Confirmed round {S.round} · rehearsing again")
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

# =================== right column: where you stand · next up · versions + activity ===================
with right:
    n_mem = len(brain_agent.recall())
    md('<div class="rc-eyebrow">Where you stand</div>'
       f'<div class="rc-stand">v{2 if S.get("saved") else 1}<small>deposit rule</small></div>'
       f'<div class="rc-sub">{n_mem} correction(s) in memory · 6 assistants read this Brain</div>')
    nxt = {1: ("Teach your Brain", "the deposit reply above isn't how you'd say it"),
           2: ("Confirm the change", "nothing is saved until you do; then every assistant rehearses before it goes live"),
           3: ("Rehearse every assistant", "before anything goes live"),
           4: ("Ready to go live", "every assistant passed") if all_right else ("Fix it", "a rehearsal row came back wrong; your Brain reads the judge's reason and proposes again")}[stage]
    md('<div class="rc-eyebrow">Next up</div>' + f'<div class="rc-next">{nxt[0]}<small>{nxt[1]}</small></div>')
    if stage == 3 and S.get("boxes"):
        md('<div class="rc-eyebrow">Your Brain is on it</div><div class="rc-sub" style="margin-top:0">Seven Daytona sandboxes, one per assistant, deleted after.</div>')
    md('<div class="rc-eyebrow">Versions + activity</div>'
       + (f'<div class="rc-row"><span><b>v2</b>deposit rule — {len(S.proposal["changes"])} changes</span><span>today</span></div>' if S.get("saved") else '')
       + '<div class="rc-row"><span><b>v1</b>$20 deposit, pay any time</span><span>before</span></div>'
       + "".join(f'<div class="rc-row"><span>{t}</span><span>{when}</span></div>' for t, when in S.log))
