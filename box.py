"""box.py — the Daytona part, built at the event (18 Oct 2026, 15:00–17:00).

One prepared world, forked once per scenario, run in parallel, judged on the laptop, deleted.

  make_box(d)           a fresh sandbox with the prototype uploaded (nothing to install)
  rehearse_in_boxes(v)  one box per scenario, all in parallel: run rehearse_one.py inside,
                        collect one JSON line each, delete; returns {id: {"reply","actions","box","seconds"}}
  (fork was the plan; this account's sandbox type doesn't support it, so each scenario gets a fresh box)

The model key goes into each box as an environment variable for the run and dies with the box.
"""
import json, os, time
from concurrent.futures import ThreadPoolExecutor
from daytona import Daytona

APP = "/home/daytona/app"
FILES = ["assistant.py", "brain_agent.py", "rehearse_one.py", "brain.json", "guests.json", "world/services.py"]
OPTIONAL = ["corrections.jsonl"]            # the correction memory, when one exists
SCENARIOS = [g["id"] for g in json.load(open("guests.json"))]

def _env() -> dict:
    keys = ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL")
    return {k: os.environ[k] for k in keys if k in os.environ}

def make_box(d: Daytona):
    """A fresh box with the prototype inside. Nothing to install: the code uses only Python's standard library."""
    box = d.create()
    box.process.exec(f"mkdir -p {APP}/world")
    for path in FILES + [p for p in OPTIONAL if os.path.exists(p)]:
        box.fs.upload_file(open(path, "rb").read(), f"{APP}/{path}")
    return box

def _run_one(d: Daytona, scenario_id: str, version: str, env: dict) -> tuple[str, dict]:
    """One fresh box, one scenario inside it, its one JSON line back, box deleted."""
    t0 = time.time()
    clone = None
    try:
        clone = make_box(d)
        r = clone.process.exec(f"python3 rehearse_one.py {scenario_id} {version}", cwd=APP, env=env, timeout=120)
        lines = [l for l in (r.result or "").strip().splitlines() if l.strip().startswith("{")]
        if r.exit_code != 0 or not lines:
            return scenario_id, {"reply": "box error: " + (r.result or "")[-200:], "actions": [],
                                 "box": clone.id[:8], "seconds": round(time.time() - t0, 1)}
        out = json.loads(lines[-1])
        return scenario_id, {"reply": out.get("reply", ""), "actions": out.get("actions", []),
                             "box": clone.id[:8], "seconds": round(time.time() - t0, 1)}
    except Exception as e:                      # one broken clone never sinks the run
        return scenario_id, {"reply": f"box error: {e}", "actions": [],
                             "box": clone.id[:8] if clone else "-", "seconds": round(time.time() - t0, 1)}
    finally:
        if clone is not None:
            try: clone.delete()
            except Exception: pass

def rehearse_in_boxes(version: str = "v1", log=print) -> dict:
    """Seven boxes, all at once: create, upload, run one scenario each, collect, delete.
    Returns {scenario_id: {reply, actions, box, seconds}}."""
    d = Daytona()
    env = _env()
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(SCENARIOS)) as pool:
        results = dict(pool.map(lambda sid: _run_one(d, sid, version, env), SCENARIOS))
    for sid in SCENARIOS:
        log(f"  {sid}  box {results[sid]['box']}  {results[sid]['seconds']}s")
    log(f"{len(SCENARIOS)} boxes created, run and deleted · {time.time() - t0:.1f}s")
    return results

if __name__ == "__main__":
    import sys
    out = rehearse_in_boxes(sys.argv[1] if len(sys.argv) > 1 else "v1")
    for sid, r in out.items():
        print(sid, "·", r["reply"][:70], "·", [a["type"] for a in r["actions"]])
