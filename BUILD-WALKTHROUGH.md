# Build walkthrough — step by step, with an AI beside you

Every step: what you do, what you ask the AI, what you should see, what to do if not.
Keep one terminal open in `~/gitrepo/hacksprint-seoul`. Every command starts with
`doppler run -- .venv/bin/python`. If something breaks, paste the full error to the AI and say
"explain this in plain words, then fix only this".

```
 TONIGHT                                   TOMORROW 15:00–17:00
 ┌───────────────────────────────┐         ┌───────────────────────────────┐
 │ 0 keys in .env                │         │ 6 box.py: base box + upload   │
 │ 1 smoke.py passes             │         │ 7 fork ×7, run, collect       │
 │ 2 run.py offline passes       │  ────►  │ 8 wire --boxes into run.py    │
 │ 3 run.py live model passes    │         │ 9 rehearse twice, record      │
 │ 4 rehearse_one.py t1 live     │         │10 README "built at event"     │
 │ 5 read every file once        │         └───────────────────────────────┘
 └───────────────────────────────┘
```

## Tonight

### 0. Keys
Copy `.env.example` to `.env`. Paste `DAYTONA_API_KEY` (app.daytona.io → API keys) and
`LLM_API_KEY` (OpenRouter). Never commit `.env` (it's gitignored; check with `git status`).

### 1. The box works
Run `doppler run -- .venv/bin/python smoke.py`. See four timed lines and `PASS` under 30 s.
If `SLOW`: ask the AI "make a Daytona snapshot with openai and python-dotenv preinstalled
and use it in smoke.py". If an auth error: the key is wrong or not loaded; `cat .env`.

### 2. The loop works offline
`LLM_FAKE=1 doppler run -- .venv/bin/python run.py`. Type the correction (or press Enter for the default),
answer `y` twice. See: the wrong reply, your correction, the proposal, a 7-row table with
one ✗ (g4), a second proposal, a clean table, "Support is ready".
Then `cp fixtures/brain.original.json brain.json` to reset the Brain for next time.

### 3. The loop works with the real model
`doppler run -- .venv/bin/python run.py`. Same flow, but Gemini writes the replies. Expect differences:
- A reply passes or fails on words. If a correct reply fails on wording (e.g. says
  "thirty percent"), loosen `reply_must` in `guests.json` to a word that will always be
  there, or add alternatives. Ask the AI: "g2 failed on wording, here is the reply; make
  the check robust without making it meaningless."
- If the model doesn't press a button (no `payment_link` for g3), tighten the prompt in
  `assistant.py` RULES. Ask: "the model answered but took no action for g3; make the
  instruction about actions unambiguous."
- If the correction proposal only changes `deposit` and not the FAQ, that's the demo
  working as designed: round 2 catches it.
Run it twice. Reset the Brain between runs.

### 4. One scenario, standalone
`doppler run -- .venv/bin/python rehearse_one.py t1 v1` → one JSON line with `release_hold`.
This is exactly what each box runs tomorrow.

### 5. Read every file once
Ask the AI, file by file: "explain assistant.py to me in plain words, 10 lines max".
You must be able to say what each file does in one sentence.

## Tomorrow, 15:00–17:00 (the Daytona part — built live)

### 6. box.py, part one: a base box with the world inside (15:00–15:25)
Ask the AI, with TECH-SPEC.md §4 open:
"Write box.py. Function prepare_base(): create a Daytona sandbox, upload these files into
/home/daytona/app keeping paths: assistant.py, rehearse_one.py, brain.json, guests.json,
world/services.py, fixtures/*.json; then exec `pip install -q openai python-dotenv` in
that folder. Print the box id and seconds. Return the sandbox."
Test: `doppler run -- .venv/bin/python -c "import box; b=box.prepare_base(); print(b.id); b.delete()"`.

### 7. box.py, part two: fork, run, collect (15:25–16:00)
Ask: "Add run_all(base, version): for each scenario id in guests.json, fork the base,
exec `python3 rehearse_one.py <id> <version>` in /home/daytona/app with env LLM_API_KEY,
LLM_MODEL, LLM_BASE_URL from my .env, parse the last stdout line as JSON, delete the fork.
Run the seven in parallel with a thread pool. Print box id and seconds per scenario.
Return {id: {'reply':..., 'actions':[...]}}. On any exception for one scenario, return
{'reply': 'box error: ...', 'actions': []} and keep going."
Test: `doppler run -- .venv/bin/python -c "import box,json; b=box.prepare_base(); print(json.dumps(box.run_all(b,'v1'),indent=1)); b.delete()"`.
Open the Daytona dashboard: you should see boxes appear and disappear.
If `fork` errors: ask "fall back to creating 7 sandboxes and uploading the files to each".

### 8. Wire it in (16:00–16:20)
Ask: "In run.py add a --boxes flag. When set, rehearse() calls box.run_all instead of the
laptop loop. Prepare the base once at the start and delete it at the end. Everything else
unchanged." Test: `doppler run -- .venv/bin/python run.py --boxes`.

### 9. Rehearse the demo (16:20–16:45)
Full run twice with the dashboard visible. Record the better one (QuickTime, screen).
Save that run's output: redirect to `replay.txt`. Reset the Brain after each run.

### 10. Close (16:45–17:00)
README → "Built at the event": box.py (prepare, fork ×7, parallel run, collect, delete),
the --boxes flag. Commit. Breathe.

## The three minutes
0:00 "This assistant books guests and takes deposits. The founder teaches it once. Before
     that goes live, it rehearses in seven cloned sandboxes. Here's what it caught."
0:20 step 1–3 (wrong reply, her sentence, confirm)
1:00 `--boxes` run; dashboard shows seven boxes; table appears; one ✗
2:00 round 2, confirm, rerun, all ✓, "Support is ready"
2:40 "Fake studio. Prepared the loop last night; the sandbox part was built this afternoon.
     MystFlo: working demos, no paying users. This check is designed, not built. Yet."

## If it breaks on stage
1. `LLM_FAKE=1 doppler run -- .venv/bin/python run.py` — "this is the cached rehearsal from an hour ago".
2. The screen recording.
3. `cat replay.txt`.
