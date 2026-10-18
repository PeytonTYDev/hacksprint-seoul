"""Run ONE scenario, anywhere: on this laptop, or inside a Daytona sandbox.

Starts the fake world, hands the scenario to the assistant, prints one JSON line:
  {"id": ..., "reply": ..., "actions": [...]}
The checker and the scoreboard stay on the laptop. Nothing in here is Daytona-specific,
which is the point: the box runs exactly what the laptop runs.

  python rehearse_one.py c1            # live model (LLM_API_KEY in env)
  LLM_FAKE=1 python rehearse_one.py c1 # offline
"""
import json, os, subprocess, sys, time

def main(scenario_id: str, version: str = "v1"):
    if os.path.exists("ledger.jsonl"): os.remove("ledger.jsonl")
    world = subprocess.Popen([sys.executable, "world/services.py"])
    try:
        import assistant
        assistant.wait_for_services()
        brain = json.load(open("brain.json"))
        g = next(x for x in json.load(open("guests.json")) if x["id"] == scenario_id)
        text = g.get("message") or "EVENT (no guest message): " + json.dumps(g["event"])
        r = assistant.handle(brain, g["id"], text, fake_key=f"{version}:{g['id']}", who=(g["assistant"], g["role"]))
        print(json.dumps({"id": g["id"], **r}))
    finally:
        world.terminate()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "v1")
