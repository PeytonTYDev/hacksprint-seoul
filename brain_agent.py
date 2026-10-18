"""The Brain agent's correction capability: founder feedback → proposed Brain changes, shown before anything is saved; confirmed corrections are remembered.

The founder speaks plainly ("No. 30% at booking or the spot isn't held").
The model turns that into exact field changes. She confirms; only then it's saved.
The correction memory: every learned correction is injected into every assistant's prompt as a hard rule."""
import json, os, re

PROMPT = """A founder corrected her assistant. Turn the correction into exact changes to her BRAIN (JSON).
Change every place the old rule appears, including FAQ answers. Keep her voice.
Reply with JSON only: {{"summary": "...", "changes": [{{"path": "deposit", "new": "..."}}, {{"path": "faq.0.a", "new": "..."}}]}}
Paths are dotted; list indexes are numbers.

BRAIN:
{brain}

FOUNDER SAID: {feedback}"""

def propose(brain: dict, feedback: str, fake_key: str | None = None) -> dict:
    if os.getenv("LLM_FAKE") == "1":
        return json.load(open("fixtures/fake_corrections.json"))[fake_key]
    import assistant
    text = assistant.chat("You turn a founder's correction into exact JSON changes to her Brain.",
                          PROMPT.format(brain=json.dumps(brain, indent=1), feedback=feedback))
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0))

MEMORY = "corrections.jsonl"      # the learned corrections: hard rules, always injected, newest wins

def remember(feedback: str, proposal: dict) -> None:
    """Commit the confirmed correction as a record: who said what, when, and the rule."""
    import json as _j, time as _t
    with open(MEMORY, "a") as f:
        f.write(_j.dumps({"at": _t.strftime("%Y-%m-%d %H:%M"), "founder_said": feedback,
                          "rule": proposal["summary"], "changes": proposal["changes"]}) + "\n")

def recall() -> list[dict]:
    import json as _j, os as _o
    return [_j.loads(l) for l in open(MEMORY)] if _o.path.exists(MEMORY) else []

def apply(brain: dict, changes: list[dict]) -> dict:
    out = json.loads(json.dumps(brain))                   # copy, never edit the original in place
    for c in changes:
        node, keys = out, c["path"].split(".")
        for k in keys[:-1]:
            node = node[int(k)] if isinstance(node, list) else node[k]
        last = keys[-1]
        if isinstance(node, list): node[int(last)] = c["new"]
        else: node[last] = c["new"]
    return out
