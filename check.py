"""Plain code marks the rehearsal. Not the AI marking itself.

For each guest: must the reply contain these words, must it NOT contain those,
and what must the ledger show (what was actually booked / linked)."""

def check(guest: dict, result: dict) -> tuple[bool, str]:
    reply = result["reply"].lower()
    for w in guest.get("reply_must", []):
        if w.lower() not in reply:
            return False, f'reply missing "{w}"'
    for w in guest.get("reply_must_not", []):
        if w.lower() in reply:
            return False, f'reply still says "{w}" (old)'
    for kind, want in guest.get("ledger_must", {}).items():
        hits = [a for a in result["actions"] if a["type"] == kind]
        if not hits:
            return False, f"no {kind} action was taken"
        for k, v in want.items():
            if hits[-1].get(k) != v:
                return False, f"{kind}.{k} was {hits[-1].get(k)}, expected {v}"
    return True, "ok"
