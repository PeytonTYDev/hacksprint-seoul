# The agent — system card (prototype of MystFlo's Brain agent, correction capability)

```
                       founder's one sentence
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ BRAIN AGENT (brain_agent.py + run.py)                                        │
 │  1 CAPTURE     the reply/action she flagged                              │
 │  2 RECOMMEND   exact field changes, every place the old rule hides        │
 │  3 REVIEW      she confirms / edits / rejects — nothing saves without it  │
 │  4 COMMIT      Brain fields updated + a learned-correction RECORD         │
 │  5 PROVE       rehearsal in cloned sandboxes, plain-code judged (Daytona) │
 │  6 INJECT      every later reply/action reads Brain + corrections         │
 └──────────────┬───────────────────────────────────────────────┬───────────┘
                │ reads/writes                                  │ runs
                ▼                                               ▼
 ┌─────────────────────────┐   ┌──────────────────┐   ┌────────────────────────┐
 │ BRAIN  brain.json       │   │ MEMORY           │   │ ASSISTANT assistant.py │
 │ = brain_profile fields  │   │ corrections.jsonl│   │ Brain + corrections +  │
 │   services, policies,   │   │ = brain_          │   │ message/event → model  │
 │   faqs, brand voice     │   │   corrections     │   │ → reply + actions      │
 └─────────────────────────┘   └──────────────────┘   └───────────┬────────────┘
                                                                  │ presses
                                                                  ▼
                                              ┌─────────────────────────────────┐
                                              │ TOOLS (fake, inside each box)   │
                                              │ payment link · calendar hold ·  │
                                              │ refund · Luma listing · email   │
                                              └─────────────────────────────────┘
```

## What it does
Takes a founder's correction in plain words, proposes the exact Brain changes (every place
the old rule appears), saves only on her confirm, commits the correction as a durable record,
then proves the change across replies, generated content and operations before the assistant
goes live. This is ADR-023's loop (capture → recommend → review → commit → inject) with
#5519's rehearsal as the proof step.

## Brain fields it references
| prototype (`brain.json`) | MystFlo `brain_profile` (field registry) |
|---|---|
| `classes.*` prices, times | `services` (keyed-array, section `sell`) |
| `deposit`, `refunds` | `policies` / `ops_policies` (keyed-map, section `run`) |
| `faq[]` | `faqs` (keyed-array, section `faqs`) |
| `voice` | `brand_voice_v2` (section `branding`) |
| `business` | `business_name`, `location` |
Correction proposals name a dotted path per change; in MystFlo these become field-registry
keys with sub-keys (`policies.deposit`, `faqs[question]`).

## Tools it is connected to (fake here, Connects in MystFlo)
| button | fake service | MystFlo |
|---|---|---|
| `payment_link` | `world/services.py` → ledger | Stripe payment link via the wallet/billing rail |
| `book`, `keep_hold`, `release_hold` | ledger | calendar / records sheet |
| `refund`, `no_refund` | ledger | Stripe refund |
| `publish_event` | ledger | Luma |
| `draft_email` | ledger (never sent) | email draft |
The model never calls a tool itself; it returns actions, code presses buttons. Which tool,
which column, which currency are code decisions, never the model's.

## LLM
`google/gemini-3.1-flash-lite` via OpenRouter (MystFlo's live guest-chat model), temperature
0, JSON out. Correction proposals use the same model here; in MystFlo they'd ride the premium
Brain chain. Endpoint and model are two env vars (`LLM_BASE_URL`, `LLM_MODEL`).

## Memory and context
- Memory 1, the Brain: `brain.json` (= `brain_profile`). Facts, prices, policies, FAQs, voice.
- Memory 2, learned corrections: `corrections.jsonl` (= ADR-023 `brain_corrections`). One record
  per confirmed correction: when, what she said, the rule, the field changes. Injected into
  every call as hard rules, newest wins. Never written without her confirm.
- Context per call: the whole Brain + all corrections + one guest message or one event.
  No conversation history in the prototype (MystFlo keeps multi-turn history per guest).
- Not memory: the model. It is stateless; swap it and nothing is lost.

## Evaluation (Daytona)
One world prepared (files, deps), forked once per scenario, run in parallel, deleted.
Judged by `check.py` only: reply must contain / must not contain, ledger must show.
Verdict: all pass → "Support is ready"; any fail → the agent proposes again, she confirms,
rerun. The rehearsal answers the one question a diff can't: did the correction reach
everything the assistant says and does?

## What "gets smarter" means here (and only this)
The next reply cannot repeat a mistake she corrected. No weights move, nothing learns on its
own, nothing is saved without her tap. Say "taught once, remembered, proven." Never "learns
every cycle."
