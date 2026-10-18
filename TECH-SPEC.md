# Tech spec — Get Support ready (prototype)

## 1. Components

```
 LAPTOP                                          DAYTONA
 ┌────────────────────────────────┐              ┌──────────────────────────────┐
 │ run.py        the loop, UI     │   prepare    │ BASE box                     │
 │ brain_agent.py    feedback→changes │ ───────────► │  files + pip install         │
 │ check.py      marks results    │              └──────────────┬───────────────┘
 │ guests.json   7 scenarios      │                     fork ×7 │
 │ brain.json    the Brain        │              ┌──────┬──────┬┴─────┬──────┐
 │ box.py (event) orchestration   │   exec       │ g2   │ g3   │ ...  │ t2   │
 │                                │ ───────────► │ rehearse_one.py <id>        │
 │                                │ ◄─────────── │  world/services.py inside   │
 │                                │  json line   │  assistant.py inside        │
 └────────────────────────────────┘              └─────────────────────────────┘
                                                  delete all 8
```

| file | runs where | role |
|---|---|---|
| `run.py` | laptop | steps 1–5, scoreboard, confirm prompts |
| `brain_agent.py` | laptop | model turns feedback into `{summary, changes[{path,new}]}`; `apply()` patches a copy |
| `check.py` | laptop | pure functions: reply_must / reply_must_not / ledger_must |
| `rehearse_one.py` | laptop or box | starts the fake world, runs one scenario, prints one JSON line |
| `assistant.py` | laptop or box | Brain → model → `{reply, actions}`; presses buttons via HTTP |
| `world/services.py` | laptop or box | HTTP server; any POST `/kind` appends to `ledger.jsonl` |
| `box.py` | laptop (event) | Daytona: create base, upload, install, fork ×7, exec, collect, delete |

## 2. Data shapes
Scenario (`guests.json`): `{id, message | event+label, reply_must[], reply_must_not[], ledger_must{kind:{field:value}}}`
Model output: `{"reply": str, "actions": [{"type": book|payment_link|keep_hold|release_hold|refund|no_refund|publish_event|draft_email, ...}]}`
Ledger line: `{"type": kind, "guest": id, ...fields, "url"?}`
Correction: `{"summary": str, "changes": [{"path": "deposit" | "faq.0.a", "new": str}]}`
Result line (from a box): `{"id", "reply", "actions": [ledger entries]}`

## 3. Model
OpenAI-compatible client. Defaults: `LLM_BASE_URL=https://openrouter.ai/api/v1`,
`LLM_MODEL=google/gemini-3.1-flash-lite` (MystFlo's live guest-chat model). `LLM_API_KEY`
from `.env`. Swap to any OpenAI-compatible endpoint (e.g. a Nosana one) by changing the two vars.
`temperature=0`. JSON pulled from the first `{...}` block. `LLM_FAKE=1` → fixtures.

## 4. Daytona (SDK 0.225.0, verified signatures)
```python
from daytona import Daytona
d = Daytona()                                   # DAYTONA_API_KEY from env
base = d.create()                               # default image, Python available
base.fs.upload_file(bytes, "/home/daytona/app/<path>")   # per file
base.process.exec("pip install -q openai python-dotenv", cwd="/home/daytona/app")
clone = base.fork()                             # one per scenario, from the same state
r = clone.process.exec("python3 rehearse_one.py c1 v1", cwd="/home/daytona/app",
                       env={"LLM_API_KEY": key, "LLM_MODEL": model, "LLM_BASE_URL": url})
line = r.result.strip().splitlines()[-1]        # the JSON line
clone.delete(); base.delete()
```
Parallel: `concurrent.futures.ThreadPoolExecutor(max_workers=7)` over the forks.
Timing target: base prepare ≤ 20 s (once), fork + run ≤ 30 s for all seven together.
If `fork` is unavailable on the plan: create 7 boxes from the base's snapshot, or create
7 plain boxes and upload to each (slower, same result).
Model key inside the box: acceptable for the hackathon; in production the rehearsal runs
in MystFlo's backend and no key leaves it.

## 5. Checks (pure)
- `reply_must`: every string present (case-insensitive)
- `reply_must_not`: none present → catches old values (e.g. "$20")
- `ledger_must`: last action of that kind exists and matching fields equal

## 6. Failure handling
- Model returns non-JSON → treated as reply with no actions → scenario fails with a clear "why".
- Box exec error → scenario marked ✗ "box error: …", run continues.
- Any failure after round 3 → "Not ready", Support stays off.
- Offline: `LLM_FAKE=1` fixtures keyed `v0|v1|v2:<id>`.

## 7. Security / honesty
Fake data only. `.env` gitignored. Nothing sent. Drafts never send. No MystFlo secrets
or production code in this repo.
