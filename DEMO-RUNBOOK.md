# Demo runbook — Teach the Brain once

## Before you present, once
1. Terminal: `cd ~/gitrepo/hacksprint-seoul && ./reset.sh`
2. Start the page: `doppler run -- .venv/bin/streamlit run app.py` (a browser tab opens; leave the terminal running)
3. Second tab: Daytona dashboard, logged in, sandboxes list visible
4. Third tab: the deck

## The three minutes
| time | do | say |
|---|---|---|
| 0:00 | deck, slide 1 | a founder's knowledge sits in a static document; the assistants never learn from her corrections; the next guest is the test |
| 0:20 | slide 2 | she teaches one Brain agent; six assistants read that Brain; seven sandboxes prove it before any guest hears it |
| 0:40 | page, step 1 already on screen | a guest asks to pay on the day; Support says sure; not how Hana runs her studio |
| 1:00 | step 2: type the correction (or keep the default), click Teach | she tells the Brain agent, in her own words |
| 1:15 | step 3: proposal with three changes; click Confirm and save | the agent found the old rule in three places; nothing saves until she confirms; saved and remembered |
| 1:30 | step 4: click Rehearse every assistant; switch to the Daytona tab while it runs | seven assistants rehearse, each in its own cloned box |
| 2:00 | back to the page, table filled | six wrong before, all seven right after; the refund didn't change, on purpose |
| 2:20 | the green line | she taught the Brain once; every assistant followed; nothing was sent to anyone |
| 2:40 | stay on the table | fake studio; prototype of a designed feature; loop prepared last night, sandbox part this afternoon; MystFlo: working demos, no paying users |

If a row fails after the correction: click "Ask the agent what else to change", then "Confirm and rehearse again". Say: it missed one; the agent asks, she confirms, rerun.

## Between rehearsals
"Reset demo" at the bottom of the page, or Ctrl+C in the terminal and `./reset.sh`.

## Backups, in order
1. Wifi or model dies: Ctrl+C, then `LLM_FAKE=1 doppler run -- .venv/bin/streamlit run app.py` ("cached from the rehearsal an hour ago")
2. Streamlit misbehaves: `./reset.sh && doppler run -- .venv/bin/python run.py` (Enter, then y)
3. Screen recording
4. The printed table

## Judge answers
- Why not Notion? Notion stores the playbook; it doesn't notice the assistant said $20, and it can't rehearse.
- Doesn't Meta do this? Meta answers the message; this makes sure what it says about her business is right before a guest hears it, then does the booking and the deposit in her tools.
- Why Daytona? The assistant presses real buttons; rehearsal needs a place those buttons can't reach a real person, cloned seven times from one state.
- Why not one box? Clean state per scenario, one wait instead of seven, and the sponsor product doing what it was built for.
- Is it live? Working demos, no paying users. This check is designed, not built. Prototype.
- Does it learn? It remembers what she taught and confirmed. No weights move. Nothing saves without her tap.
