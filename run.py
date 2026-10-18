"""Get Support ready — the correction loop, end to end.

  1. a guest asks; the assistant answers in a way the founder wouldn't want
  2. the founder says, in plain words, how it should be
  3. the agent proposes exact Brain changes; the founder confirms; saved
  4. rehearsal: every guest again, before vs after; plain code marks each
  5. anything still wrong → the agent proposes again → confirm → rerun

Without --boxes the rehearsal runs on this laptop. With --boxes it runs
each guest in its own Daytona clone of one prepared world (see box.py).

  LLM_FAKE=1 .venv/bin/python run.py          # offline, canned answers (also the stage backup)
  .venv/bin/python run.py                     # live model, rehearsal on this laptop
  .venv/bin/python run.py --boxes             # live model, each scenario in its own Daytona sandbox
"""
import json, os, subprocess, sys, time
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import assistant, check, brain_agent

load_dotenv()
con = Console()
GUESTS = json.load(open("guests.json"))

def start_world():
    """The fake payment service + calendar, on this laptop."""
    if os.path.exists("ledger.jsonl"): os.remove("ledger.jsonl")
    p = subprocess.Popen([sys.executable, "world/services.py"]); assistant.wait_for_services(); return p

BOXES = "--boxes" in sys.argv          # built at the event: each scenario in its own Daytona sandbox

def rehearse(brain: dict, version: str) -> dict:
    if BOXES:
        import box
        out = box.rehearse_in_boxes(version, log=lambda m: con.print(f"[dim]{m}[/]"))
        return {sid: (check.check(next(g for g in GUESTS if g["id"] == sid), r), r) for sid, r in out.items()}
    results = {}
    for g in GUESTS:
        r = assistant.handle(brain, g["id"], g.get("message") or "EVENT (no guest message): " + json.dumps(g["event"]), fake_key=f"{version}:{g['id']}", who=(g["assistant"], g["role"]))
        results[g["id"]] = (check.check(g, r), r)
    return results

def scoreboard(before: dict, after: dict, title: str):
    t = Table(title=title)
    t.add_column("assistant"); t.add_column("scenario"); t.add_column("before (old Brain)"); t.add_column("after (taught)"); t.add_column("why")
    if BOXES: t.add_column("sandbox")
    for g in GUESTS:
        (okb, _), _ = before[g["id"]]; (oka, why), ra = after[g["id"]]
        row = [g["assistant"], (g.get("message") or g["label"])[:34], "right" if okb else "wrong", "[green]right[/]" if oka else "[red]wrong[/]", "" if oka else why]
        if BOXES: row.append(f"{ra.get('box', '-')} · {ra.get('seconds', '')}s")
        t.add_row(*row)
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
        proposal = brain_agent.propose(brain, feedback, fake_key="round1")
        if not confirm(proposal): con.print("Not saved. Nothing changes."); return
        before = rehearse(brain, "v0")
        brain = brain_agent.apply(brain, proposal["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
        brain_agent.remember(feedback, proposal)
        con.print(f"[green]Saved to the Brain.[/] Correction memory now holds {len(brain_agent.recall())} learned correction(s).")

        con.rule("[bold]4. Rehearsal before going live")
        after = rehearse(brain, "v1")
        passed = scoreboard(before, after, "she taught the Brain once · six assistants followed")

        rnd = 2
        while passed < len(GUESTS) and rnd <= 3:
            con.rule(f"[bold]5. Still wrong somewhere, round {rnd}")
            failures = "; ".join(f"{g['id']}: {after[g['id']][0][1]}" for g in GUESTS if not after[g["id"]][0][0])
            proposal = brain_agent.propose(brain, f"Rehearsal failures: {failures}. Original correction: {feedback}", fake_key=f"round{rnd}")
            if not confirm(proposal): break
            brain = brain_agent.apply(brain, proposal["changes"]); json.dump(brain, open("brain.json", "w"), indent=2)
            brain_agent.remember(feedback, proposal)
            before, after = after, rehearse(brain, f"v{rnd}")
            passed = scoreboard(before, after, f"rerun, round {rnd}")
            rnd += 1

        con.rule()
        if passed == len(GUESTS):
            con.print("[bold green]Every assistant is ready.[/] She taught the Brain once. Every assistant followed, proven before going live. Nothing was sent to anyone.")
        else:
            con.print("[bold red]Not ready.[/] Support stays off until every guest passes.")
    finally:
        world.terminate()

if __name__ == "__main__":
    main()
