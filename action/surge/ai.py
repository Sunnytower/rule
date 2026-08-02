from _common import load_rules, write_rules


sources = (
    "https://ruleset.skk.moe/List/non_ip/ai.conf",
    "https://ruleset.skk.moe/List/non_ip/apple_intelligence.conf",
)
rules = load_rules(
    sources,
    deny={"URL-REGEX", "IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
write_rules(
    "ai.list",
    "AI and Apple Intelligence",
    sources,
    rules,
    ("Place before apple_direct.list because Apple Intelligence uses an ls.apple.com hostname.",),
    "AGPL-3.0",
)
