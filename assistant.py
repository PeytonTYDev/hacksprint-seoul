"""The stand-in Support assistant.

Same shape as the live one: the Brain is handed to the model whole, the model
answers in the founder's voice and DECIDES actions; this code presses the buttons
(fake payment service + fake calendar). The model never touches a service itself.

Model: by default google/gemini-3.1-flash-lite through OpenRouter, the same
model MystFlo's live guest chat uses. LLM_BASE_URL / LLM_MODEL in .env swap it.
LLM_FAKE=1 answers from fixtures/fake_replies.json (offline rehearsal + backup).
"""
import json, os, re, urllib.request
from dotenv import load_dotenv
load_dotenv()

SERVICES = os.getenv("SERVICES_URL", "http://127.0.0.1:8787")

RULES = """You are the WhatsApp assistant for {business}. Voice: {voice}.
Answer ONLY from the BRAIN below. If the Brain does not cover it, say you will check with the owner.
Never invent prices or policies. Keep replies under 60 words.
If the guest wants to book, add a "book" action and a "payment_link" action for the deposit
that the Brain's deposit rule requires for that booking.
Some inputs are EVENTS, not guest messages. Nobody is chatting; you decide an operational action
from the Brain's rules and "reply" is a one-line note for the owner's log.
  hold_review   → "keep_hold" (name) if the Brain says the spot is held, else "release_hold" (name)
  cancellation  → "refund" (name, amount) per the Brain's refund rule, or "no_refund" (name)
  event_listing → "reply" is the full listing text (price, time, deposit rule, what to bring);
                  action "publish_event" (name, price, deposit_rule)
  email_draft   → "reply" is the email body (class, time, people, deposit amount due per the Brain);
                  action "draft_email" (to, subject). A draft is never sent.
Work every amount out from the Brain's deposit and refund rules and prices.
Reply with JSON only: {{"reply": "...", "actions": [ {{"type":"book","name":"...","class":"...","people":N}},
{{"type":"payment_link","amount":NUMBER,"for":"name"}}, {{"type":"keep_hold","name":"..."}}, {{"type":"release_hold","name":"..."}},
{{"type":"refund","name":"...","amount":NUMBER}}, {{"type":"no_refund","name":"..."}},
{{"type":"publish_event","name":"...","price":NUMBER,"deposit_rule":"..."}}, {{"type":"draft_email","to":"...","subject":"..."}} ]}} (actions may be empty).

BRAIN:
{brain}

FOUNDER CORRECTIONS (hard rules; always apply; the newest wins over anything above):
{corrections}"""

def _corrections_block() -> str:
    import correct
    rules = correct.recall()
    return "\n".join(f"- {r['at']}: {r['rule']}" for r in rules) or "- none yet"

def ask_model(brain: dict, message: str, fake_key: str | None = None) -> dict:
    if os.getenv("LLM_FAKE") == "1":
        canned = json.load(open("fixtures/fake_replies.json"))
        return canned[fake_key]
    from openai import OpenAI
    client = OpenAI(base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
                    api_key=os.getenv("LLM_API_KEY"))
    r = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "google/gemini-3.1-flash-lite"),
        messages=[{"role": "system", "content": RULES.format(business=brain["business"],
                   voice=brain["voice"], brain=json.dumps(brain, indent=1),
                   corrections=_corrections_block())},
                  {"role": "user", "content": message}],
        temperature=0)
    text = r.choices[0].message.content
    m = re.search(r"\{.*\}", text, re.S)               # pull the JSON out of any wrapper
    return json.loads(m.group(0)) if m else {"reply": text, "actions": []}

def press(kind: str, payload: dict, guest: str) -> dict:
    req = urllib.request.Request(f"{SERVICES}/{kind}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", "X-Guest": guest})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

def handle(brain: dict, guest_id: str, message: str, fake_key: str | None = None) -> dict:
    """One guest message in → reply out, buttons pressed on the way."""
    out = ask_model(brain, message, fake_key)
    done = [press(a["type"], {k: v for k, v in a.items() if k != "type"}, guest_id)
            for a in out.get("actions", []) if a.get("type") in ("book", "payment_link", "keep_hold", "release_hold", "refund", "no_refund", "publish_event", "draft_email")]
    return {"reply": out.get("reply", ""), "actions": done}
