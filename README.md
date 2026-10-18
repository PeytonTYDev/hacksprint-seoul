# Teach the Brain once — one Brain agent, six assistants, seven sandboxes

Public repo: https://github.com/PeytonTYDev/hacksprint-seoul · Keys live in Doppler, never here.

Hackathon prototype (Daytona HackSprint Seoul, 2026-10-18) of MystFlo issue #5519.
After the founder teaches the Brain, and before that goes live, every assistant rehearses on fake guests,
each in its own Daytona sandbox, and plain code checks the answers against the Brain.

Fake studio, fake guests, fake payment and calendar. Nothing is sent to anyone.
MystFlo today: working demos, no paying users. This check is designed, not built.

## Built the night before (disclosed)
- the loop, the page, the fake world, the checker, the correction memory, smoke.py

## Built at the event (18 Oct 2026, 15:00–17:00)
- `box.py` — one fresh Daytona sandbox per assistant, all seven in parallel: create, upload the prototype,
  run `rehearse_one.py` inside, collect one JSON line each, delete. ~7.5 s for seven boxes.
  (Fork was the plan; this account's sandbox type doesn't support it, so each scenario gets a fresh box.)
- `--boxes` in `run.py` and the sandbox toggle in `app.py`: the before/after rehearsal runs in Daytona,
  box ids and seconds on the scoreboard. Dropped the `openai` SDK for plain HTTP so boxes need nothing installed.
