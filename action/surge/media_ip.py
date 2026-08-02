from _common import load_rules, write_rules


sources = ("https://ruleset.skk.moe/List/ip/stream.conf",)
rules = load_rules(sources, allow={"IP-CIDR", "IP-CIDR6", "IP-ASN"})
write_rules(
    "media_ip.list",
    "Global Streaming Media IP",
    sources,
    rules,
    ("Place after domain rules and before china_ip.list.",),
    "AGPL-3.0",
)
