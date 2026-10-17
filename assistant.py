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
Reply with JSON only: {{"reply": "...", "actions": [ {{"type":"book","name":"...","class":"...","people":N}},
{{"type":"payment_link","amount":NUMBER,"for":"name"}} ]}} (actions may be empty).

BRAIN:
{brain}"""

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
                   voice=brain["voice"], brain=json.dumps(brain, indent=1))},
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
            for a in out.get("actions", []) if a.get("type") in ("book", "payment_link")]
    return {"reply": out.get("reply", ""), "actions": done}
