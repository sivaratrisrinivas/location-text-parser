from .rules import parse_source as parse_rules
from .merge import merge

def parse(texts, engine="rules"):
    if engine == "llm":
        from .llm import parse_source as p
    else:
        p = parse_rules
    return merge([p(t) for t in texts])
