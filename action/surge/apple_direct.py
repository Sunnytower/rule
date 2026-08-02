from _common import write_rules


rules = [
    "DOMAIN-SUFFIX,ls.apple.com",
    "DOMAIN-SUFFIX,store.apple.com",
]
write_rules(
    "apple_direct.list",
    "Apple Maps Weather Location Direct",
    (),
    rules,
    ("Keep ai.list before this ruleset.",),
)
