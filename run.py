"""Get Support ready — the correction loop, end to end.

  1. a guest asks; the assistant answers in a way the founder wouldn't want
  2. the founder says, in plain words, how it should be
  3. the agent proposes exact Brain changes; the founder confirms; saved
  4. rehearsal: every guest again, before vs after; plain code marks each
  5. anything still wrong → the agent proposes again → confirm → rerun

Tonight the rehearsal runs on this laptop. Tomorrow, at the event, --boxes runs
each guest in its own Daytona clone of one prepared world (see box.py).

  LLM_FAKE=1 .venv/bin/python run.py          # offline, canned answers (also the stage backup)
  .venv/bin/python run.py                     # live model
"""
import json, os, subprocess, sys, time
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import assistant, check, correct

load_dotenv()
con = Console()
GUESTS = json.load(open("guests.json"))

def start_world():
    """The fake payment service + calendar, on this laptop for tonight."""
    if os.path.exists("ledger.jsonl"): os.remove("ledger.jsonl")
    p = subprocess.Popen([sys.executable, "world/services.py"]); time.sleep(0.5); return p

def rehearse(brain: dict, version: str) -> dict:
    results = {}
    for g in GUESTS:
        r = assistant.handle(brain, g["id"], g.get("message") or "EVENT (no guest message): " + json.dumps(g["event"]), fake_key=f"{version}:{g['id']}", who=(g["assistant"], g["role"]))
        results[g["id"]] = (check.check(g, r), r)
    return results

def scoreboard(before: dict, after: dict, title: str):
    t = Table(title=title)
    t.add_column("assistant"); t.add_column("scenario"); t.add_column("before"); t.add_column("after"); t.add_column("why")
    for g in GUESTS:
        (okb, _), _ = before[g["id"]]; (oka, why), _ = after[g["id"]]
        t.add_row(g["assistant"], (g.get("message") or g["label"])[:34], "✓" if okb else "✗", "[green]✓[/]" if oka else "[red]✗[/]", "" if oka else why)
    con.print(t)
    return sum(1 for g in GUESTS if after[g["id"]][0][0])

def confirm(proposal: dict) -> bool:
    con.print(f"\n[bold]Agent proposes:[/] {proposal['summary']}")
    for c in proposal["changes"]:
        con.print(f"  [dim]{c['path']}[/] → {c['new']}")
    return input("Save this to the Brain? [y/n] ").strip().lower() == "y"

def main():
    world = start_world()
    try:
        brain = json.load(open("brain.json"))
        con.rule("[bold]1. A guest asks")
        g2 = next(x for x in GUESTS if x["id"] == "g2")
        r = assistant.handle(brain, g2["id"], g2["message"], fake_key="v0:g2", who=(g2["assistant"], g2["role"]))
        con.print(f"[cyan]guest:[/] {g2['message']}\n[magenta]assistant:[/] {r['reply']}")

        con.rule("[bold]2. The founder corrects it")
        feedback = input("Founder: ").strip() or "No. 30% deposit at booking, or the spot isn't held."
        con.print(f"[yellow]founder:[/] {feedback}")

        con.rule("[bold]3. Proposed Brain change")
        proposal = correct.propose(brain, feedback, fake_key="round1")
        if not confirm(proposal): con.print("Not saved. Nothing changes."); return
        before = rehearse(brain, "v0")
        brain = correct.apply(brain, proposal["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
        correct.remember(feedback, proposal)
        con.print(f"[green]Saved to the Brain.[/] Correction memory now holds {len(correct.recall())} learned correction(s).")

        con.rule("[bold]4. Rehearsal before going live")
        after = rehearse(brain, "v1")
        passed = scoreboard(before, after, "one correction · six assistants · one Brain")

        rnd = 2
        while passed < len(GUESTS) and rnd <= 3:
            con.rule(f"[bold]5. Still wrong somewhere, round {rnd}")
            failures = "; ".join(f"{g['id']}: {after[g['id']][0][1]}" for g in GUESTS if not after[g["id"]][0][0])
            proposal = correct.propose(brain, f"Rehearsal failures: {failures}. Original correction: {feedback}", fake_key=f"round{rnd}")
            if not confirm(proposal): break
            brain = correct.apply(brain, proposal["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
            correct.remember(feedback, proposal)
            before, after = after, rehearse(brain, f"v{rnd}")
            passed = scoreboard(before, after, f"rerun, round {rnd}")
            rnd += 1

        con.rule()
        if passed == len(GUESTS):
            con.print("[bold green]Support is ready.[/] Taught once, confirmed, proven across replies, content and operations. Nothing was sent to anyone.")
        else:
            con.print("[bold red]Not ready.[/] Support stays off until every guest passes.")
    finally:
        world.terminate()

if __name__ == "__main__":
    main()
