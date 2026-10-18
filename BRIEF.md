# Teach the Brain once — product brief

Daytona HackSprint Seoul, 2026-10-18. Solo. Prototype of MystFlo issue #5519 + ADR-023.

## The problem
A creative or independent founder with traction is her own operations manager. Prices, deposit rules,
refund rules, voice: all in her head, retyped in five places. When she gives that to an
AI assistant, two things go wrong. The assistant is too generous (a model defaults to
pleasing whoever is in front of it), and nobody checks what it will say or do before a
guest finds out. Every WhatsApp assistant on the market, Meta's included, answers the
guest. None lets the founder rehearse it first. In MystFlo today the test run is skipped
for WhatsApp assistants. That gap is #5519.

## The idea
The founder teaches the Brain once, in plain words; every assistant reads it live. Before that teaching goes live,
the assistant rehearses on fake guests and fake operations in cloned sandboxes, and
plain code checks every reply and every action against her Brain.

```
 1. a guest asks "can I pay the deposit on the day?"  → assistant: "sure, no problem"
 2. founder: "No. 30% at booking, or the spot isn't held."
 3. agent proposes exact Brain changes → she confirms → saved
 4. rehearsal: 3 replies · 2 content · 2 operations, each in its own cloned box
 5. one still wrong (the FAQ) → agent asks → she confirms → rerun → all pass
    "Support is ready. Taught once, confirmed, proven. Nothing was sent to anyone."
```

## What the rehearsal covers
| kind | scenario | what must change after the correction |
|---|---|---|
| reply | can I pay on the day? | says 30%, never $20 |
| reply | book for 2 (Mina) | payment link is $30, booking for 2 in the ledger |
| reply | deposit policy? | catches the FAQ still saying $20 (round 2) |
| content | Luma event listing | listing carries the 30% rule |
| content | booking confirmation email | draft says $30 due; drafts never send |
| operation | 48h unpaid, keep or release? | releases the hold (no words at all) |
| operation | cancel 10 days out, refund? | unchanged: full refund (regression check) |

## What Daytona does here
One world is prepared once: a fake payment service, a fake calendar, the assistant and
the Brain. It is forked seven times, one scenario per clone, all at once. The assistant
presses real buttons inside each clone; the buttons only reach the fake services that
live there. Replies and ledgers come back, the boxes are deleted. This is Daytona's own
"AI evaluations" case: parallel environments from one snapshot, running servers inside.
In production this check would run in MystFlo's backend; an environment like this is
what a rehearsal that acts against fake copies of real tools would need.

## Real / fake / prototype
- Real: the shape of MystFlo's Support assistant; the same model as live guest chat
  (Gemini Flash-Lite via OpenRouter); the rule that the founder confirms before anything
  is saved; the Brain file format.
- Fake: the studio (Mud & Fire Pottery, Seoul), the guests, the payment service, the
  calendar, Luma, email. Nothing is sent to anyone.
- Prototype: the assistant in the box is a small stand-in, not MystFlo production code.
  MystFlo: working demos, no paying users. #5519 and ADR-023: designed, not built.

## Built the night before (disclosed) / built at the event
- Night before: Brain, scenarios, fake world, stand-in assistant, checker, correction
  step, the loop on a laptop, offline mode (also the stage backup), Daytona smoke test.
- At the event: box.py — upload the world, start the services, fork ×7, run one
  scenario per clone, collect replies and ledgers, delete; box ids and timings on screen.

## Judging
- Completeness: the loop runs end to end, offline or live.
- Innovation: not "test the chatbot". One correction proven across replies, content and
  operations before it goes live, in cloned worlds.
- Real problem: the founder's own money and policies; the market skips this step.
- Sponsor usage: fork, parallel clones, servers inside the box.

## Say / never say
Say: taught once · confirmed · remembered for every assistant · proven before going live
· prototype of #5519 · fake studio, nothing sent.
Never: learns by itself · every cycle · the Brain learned · COO · live · sandbox = privacy
· MystFlo runs on Daytona.

## Backup ladder
live run → `LLM_FAKE=1` offline run ("cached from rehearsal") → screen recording → paper.
