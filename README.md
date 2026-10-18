# Teach the Brain once

One Brain agent. Six assistants that read the same Brain. Seven Daytona sandboxes that prove a correction
landed everywhere before a guest ever hears it.

Built for Daytona HackSprint Seoul, 18 Oct 2026. Fake studio, fake guests, fake payment and calendar.
Nothing is sent to anyone. Keys live in Doppler, never here.

## The problem
A founder's knowledge sits in a static document. The assistants that act on it never learn from her
corrections: the lesson isn't captured, isn't shared across assistants, and nobody checks it stuck.
The same mistake reaches the next guest.

## How it works
```
 guest asks ──► assistant answers from the Brain ──► founder: "not how I'd say it"
                                                            │
                                                            ▼  she teaches the Brain, one sentence
                                                   ┌────────────────┐
                                                   │  Brain agent   │ proposes exact Brain changes
                                                   │  (one model)   │ ◄──── correction memory
                                                   └───────┬────────┘       (every learned rule, newest wins)
                                                           ▼  she confirms · saved
                      ┌────────────────────────────────────┴───────────────────────────────────┐
                      │                      rehearsal, before going live                      │
                      │  7 scenarios · 6 assistants · one Daytona sandbox each · all at once    │
                      │  3 replies · 2 pieces of content · 2 silent operations                  │
                      │  plain code judges every reply and every action against the Brain      │
                      └──────────────┬─────────────────────────────────────┬───────────────────┘
                                     ▼ all right                           ▼ a miss
                                  go live                 Brain agent proposes again → confirm → rerun
```
Two gates. The founder confirms (gate 1). The rehearsal passes (gate 2). The model proposes; code presses
the buttons from a fixed list. The model never chooses tools, columns or currencies.

## Sponsors
**Daytona** is the rehearsal room. Each assistant runs its scenario in a fresh sandbox with the fake world
inside, so a pressed button can never reach a real person. Seven boxes go from nothing to results in about
eight seconds, then they are deleted. `box.py`.

**Nosana** is the engine room. The assistants call any OpenAI-compatible endpoint; point `LLM_BASE_URL`
and `LLM_MODEL` at a Nosana vLLM job and the same rehearsal runs on Nosana GPU. The page names the engine
it ran on, so two scoreboards can be compared side by side.

## Files
| file | what it is |
|---|---|
| `app.py` | the page: the Brain page as a conversation, the rehearsal scoreboard, the fix loop |
| `run.py` | the same loop in the terminal (`--boxes` = Daytona) |
| `brain_agent.py` | the Brain agent: propose changes, remember corrections, apply them |
| `assistant.py` | one assistant run: prompt from the Brain + corrections, actions pressed by code |
| `check.py` | the judge: what a reply must and must not say, what the ledger must hold |
| `box.py` | Daytona: one sandbox per scenario, in parallel, deleted after |
| `rehearse_one.py` | one scenario, anywhere: laptop or inside a sandbox |
| `world/services.py` | the fake payment, calendar and email services, writing a ledger |
| `brain.json` · `guests.json` | the fake studio's Brain · the seven scenarios |
| `smoke.py` · `reset.sh` | Daytona connection check · reset the demo |

## Run
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
doppler run -- .venv/bin/streamlit run app.py       # the page
doppler run -- .venv/bin/python run.py --boxes      # the terminal, in Daytona sandboxes
LLM_FAKE=1 .venv/bin/streamlit run app.py           # offline, from fixtures
```
Secrets: `DAYTONA_API_KEY`, `LLM_API_KEY`, optional `LLM_BASE_URL`, `LLM_MODEL`, `NOSANA_API_KEY`.
