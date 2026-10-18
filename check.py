"""Plain code marks the rehearsal. Not the AI marking itself.

For each guest: must the reply contain these words, must it NOT contain those,
and what must the ledger show (what was actually booked / linked)."""
import json

def check(guest: dict, result: dict) -> tuple[bool, str]:
    # what the assistant said AND what it produced (an email draft, a listing) are both "what it said"
    reply = (result["reply"] + " " + json.dumps(result.get("actions", []))).lower()
    for w in guest.get("reply_must", []):
        options = w if isinstance(w, list) else [w]      # a list means "any of these"
        if not any(o.lower() in reply for o in options):
            return False, f'said nothing about "{" / ".join(options)}"'
    for w in guest.get("reply_must_not", []):
        if w.lower() in reply:
            return False, f'still says "{w}" (old)'
    for kind, want in guest.get("ledger_must", {}).items():
        hits = [a for a in result["actions"] if a["type"] == kind]
        if not hits:
            return False, f"no {kind} action was taken"
        for k, v in want.items():
            if hits[-1].get(k) != v:
                return False, f"{kind}.{k} was {hits[-1].get(k)}, expected {v}"
    return True, "ok"
