"""Merge per-source fields into one record and flag disagreements."""
OPEN = {"WORLDWIDE", "NON_US", "IN"}

def india(allowed):
    if not allowed: return "unknown"
    return "yes" if OPEN & set(allowed) else "no"

def merge(per_source):
    allowed = sorted(set().union(*[p["allowed"] for p in per_source]))
    tz = sorted(set().union(*[p["timezones"] for p in per_source]))
    eng = sorted(set().union(*[p["engagement"] for p in per_source]))
    visas = {p["visa"] for p in per_source} - {"unknown"}
    verdicts = [india(p["allowed"]) for p in per_source]
    known = set(verdicts) - {"unknown"}
    conflict = len(known) > 1 or len(visas) > 1
    reasons = []
    if len(known) > 1:
        reasons.append("sources disagree on whether India is allowed: " + ", ".join(f"source {i+1}={v}" for i, v in enumerate(verdicts)))
    if len(visas) > 1: reasons.append("sources disagree on visa sponsorship")
    return {"allowed": allowed, "timezones": tz, "engagement": eng,
            "visa": visas.pop() if len(visas) == 1 else ("conflict" if visas else "unknown"),
            "india": "conflict" if len(known) > 1 else (known.pop() if known else "unknown"),
            "conflict": conflict, "conflict_reasons": reasons, "per_source": per_source}
