from _common import load_rules, write_rules


sources = (
    "https://ruleset.skk.moe/List/non_ip/apple_services.conf",
    "https://raw.githubusercontent.com/Blankwonder/surge-list/master/apple.list",
)
rules = load_rules(
    sources,
    deny={"IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
write_rules(
    "apple.list",
    "Apple Default Proxy",
    sources,
    rules,
    ("Place apple_direct.list before this ruleset.",),
    "AGPL-3.0",
)
