# PRD — Teach the Brain once (correction loop + multi-assistant rehearsal)

Hackathon prototype of MystFlo #5519 ("Get Support ready" dress rehearsal) and ADR-023
(Correction Memory). Scope here is the prototype; the production spec lives in the
MystFlo repo and is updated by PR after the event.

## 1. The picture

```
 founder notices a wrong reply or action
        │  "No. 30% at booking, or the spot isn't held."
        ▼
 ┌──────────────┐  proposes exact  ┌──────────────┐  confirm  ┌───────────┐
 │ Brain agent  │ ───────────────► │ Brain change │ ────────► │ THE BRAIN │ saved
 └──────────────┘                  └──────────────┘           └─────┬─────┘
                                                        reads ▲ ▲ ▲ ▲
                    ┌──────────────────────────────────────────┴─┴─┴─┴─────┐
                    │ REHEARSAL — one cloned sandbox per scenario, parallel │
                    │  replies · content (listing, email) · operations      │
                    │  plain code checks reply + ledger against the Brain   │
                    └──────────────────────────┬────────────────────────────┘
                                               ▼
                          all pass → "Support is ready" → may go live
                          any fail → agent asks → confirm → rerun
```

## 2. Problem
Most Brains and knowledge bases are static documents. When an AI assistant gets something
wrong, the founder fixes that one reply or edits one document, and nothing else changes.
The learning loop is broken in three places:

| break | today | with this |
|---|---|---|
| capture | she fixes the reply; the lesson is lost | her sentence becomes a correction record she approved |
| propagation | one document edited; five assistants still wrong | one Brain; every assistant reads it live |
| proof | nobody checks; the next guest is the test | per-founder evaluation in sandboxes before going live |

A human teammate is taught differently: tell them once, ask them to show you, trust them
with the next guest. Production AI assistants need the same, on the backend, per founder,
every time she teaches something. Not self-learning: the Brain remembers what she taught
and confirmed, and the rehearsal proves it. (Market: every WhatsApp assistant, Meta's
included, answers the guest; none rehearses. MystFlo skips the test run for WhatsApp
assistants today, #5519.)

## 3. Users and job
Founder (host). Job: "when my assistant gets something wrong, I say it once, and I know
it's fixed everywhere before another guest sees it."

## 4. Requirements (prototype)
| # | Requirement | Done when |
|---|---|---|
| R1 | A wrong reply is shown from the current Brain | step 1 prints a reply the founder wouldn't give |
| R2 | Founder corrects in plain words, nothing else | free-text input, one sentence |
| R3 | Agent proposes exact Brain changes; nothing saves without confirm | changes listed with paths; `y` saves, anything else aborts |
| R4 | Rehearsal covers replies, content and operations | ≥3 replies, ≥2 content, ≥2 operations from one Brain |
| R5 | Plain code marks every scenario; the AI never marks itself | `check.py` only, no model call |
| R6 | Actions are checked from a ledger, not from words | fake services log every button press |
| R7 | Each scenario runs in its own sandbox cloned from one prepared world | Daytona fork ×N, parallel |
| R8 | A miss triggers a second proposal, confirm, rerun | round 2 catches the stale FAQ |
| R9 | Regression: unrelated rules stay unchanged | refund scenario passes before and after |
| R10 | Nothing is sent to anyone; drafts never send | all services are fake; email is a draft |
| R11 | Offline mode reproduces the full loop | `LLM_FAKE=1` |
| R12 | Boxes are deleted after the run | zero sandboxes left in the dashboard |

## 5. Out of scope (prototype)
Running MystFlo's production chat handler; the WhatsApp doorway; wallet billing; the
24-hour pass validity rule from #5519; cross-founder learning; self-learning of any kind.

## 6. Say / never say
Say: taught once · confirmed · remembered for every assistant · proven before going live.
Never: learns by itself · every cycle · the Brain learned · COO · live · sandbox = privacy.

## 7. Map to MystFlo
| prototype | MystFlo |
|---|---|
| `brain.json` | `brain_profile` + "Save a copy" export |
| `brain_agent.py` | ADR-023 correction memory (proposed) + Brain agent "clarify, then confirm" |
| rehearsal + checker | #5519 steps 1–5; "answer like live chat" shared block (not built) |
| fake services | stubs of the Connects (Stripe link, calendar, Luma, email) |
| Daytona clones | optional later; production check runs in the backend first (architect ruling 2026-10-17) |
