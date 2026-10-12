"""Code checks (objective rules) run on every parser output. Each returns (passed, reason)."""
import re
TOK = re.compile(r"^(WORLDWIDE|NON_US|US|CA|UK|EUROPE|LATAM|APAC|[A-Z]{2})$")
TZ = re.compile(r"^(US|US_EAST|US_PACIFIC|EUROPE|CET|EMEA|CET±\d|UTC[+-]\d+\.\.UTC[+-]\d+|US_PACIFIC\.\.CET)$")
ENG = {"EOR", "B2B", "CONTRACTOR", "FREELANCE"}

def check_schema(p):
    for k, typ in [("allowed", list), ("timezones", list), ("engagement", list), ("visa", str), ("india", str), ("conflict", bool)]:
        if not isinstance(p.get(k), typ): return False, f"{k} missing or not {typ.__name__}"
    if bad := [t for t in p["allowed"] if not TOK.match(t)]: return False, f"unknown country tokens {bad}"
    if bad := [t for t in p["timezones"] if not TZ.match(t)]: return False, f"unknown tz tokens {bad}"
    if bad := set(p["engagement"]) - ENG: return False, f"unknown engagement {bad}"
    if p["visa"] not in ("yes", "no", "unknown", "conflict"): return False, "bad visa value"
    if p["india"] not in ("yes", "no", "unknown", "conflict"): return False, "bad india value"
    return True, "ok"

def check_conflict_consistent(p):
    """If india is 'conflict', the conflict flag must be set and carry a reason."""
    if p["india"] == "conflict" and not (p["conflict"] and p.get("conflict_reasons")):
        return False, "india=conflict but no conflict flag/reason"
    if p["conflict"] and not p.get("conflict_reasons"):
        return False, "conflict flagged without a reason"
    return True, "ok"

def check_india_derivation(p):
    """india must follow from allowed: open token -> yes, closed list -> no, empty -> unknown (single-source)."""
    if p["india"] == "conflict": return True, "ok"
    a = set(p["allowed"]); want = "yes" if a & {"WORLDWIDE", "NON_US", "IN"} else ("no" if a else "unknown")
    return (p["india"] == want, "ok" if p["india"] == want else f"india={p['india']} but allowed={sorted(a)}")

CHECKS = [check_schema, check_conflict_consistent, check_india_derivation]
