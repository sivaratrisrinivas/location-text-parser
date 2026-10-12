import json
from pathlib import Path
from locparse import parse
from evals.checks import check_schema, check_conflict_consistent, check_india_derivation

CASES = {c["id"]: c for c in json.loads((Path(__file__).parent.parent / "data/cases.json").read_text())}
GOOD = {"allowed": ["US"], "timezones": [], "engagement": [], "visa": "no", "india": "no", "conflict": False, "conflict_reasons": []}

def test_schema_pass_and_fail():
    assert check_schema(GOOD)[0]
    assert not check_schema({**GOOD, "allowed": ["Earth"]})[0]
    assert not check_schema({**GOOD, "timezones": ["sometime"]})[0]
    assert not check_schema({**GOOD, "conflict": "no"})[0]
    assert check_schema({**GOOD, "timezones": ["UTC-8..UTC+2", "CET±3"]})[0]  # borderline tokens

def test_conflict_needs_reason():
    assert not check_conflict_consistent({**GOOD, "india": "conflict", "conflict": True})[0]
    assert check_conflict_consistent({**GOOD, "india": "conflict", "conflict": True, "conflict_reasons": ["x"]})[0]

def test_india_derivation():
    assert check_india_derivation(GOOD)[0]
    assert not check_india_derivation({**GOOD, "india": "yes"})[0]
    assert check_india_derivation({**GOOD, "allowed": [], "india": "unknown"})[0]

def test_case1_matcha_india_conflict():
    c = CASES["matcha-fse"]; p = parse([s["text"] for s in c["sources"]])
    assert p["india"] == "conflict" and p["conflict"]
    assert p["per_source"][0]["allowed"] == ["BR", "CA", "EUROPE", "LATAM", "UK", "US"]
    assert "WORLDWIDE" in p["per_source"][1]["allowed"]
    assert set(p["engagement"]) == {"B2B", "EOR"}

def test_single_source_is_never_conflict():
    assert not parse(["Remote (US only). We're not able to sponsor visas."])["conflict"]

def test_visa_and_timezones():
    p = parse(["REMOTE (Germany) | We don't offer visa sponsorship. Remote, UTC-3 to UTC+3"])
    assert p["visa"] == "no" and p["allowed"] == ["DE"] and "UTC-3..UTC+3" in p["timezones"]

def test_all_rules_outputs_pass_checks():
    for c in CASES.values():
        p = parse([s["text"] for s in c["sources"]])
        for ch in (check_schema, check_conflict_consistent, check_india_derivation):
            assert ch(p)[0], (c["id"], ch.__name__, ch(p)[1])
