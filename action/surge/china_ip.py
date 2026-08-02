from _common import load_rules, write_rules


sources = (
    "https://ruleset.skk.moe/List/ip/domestic.conf",
    "https://ruleset.skk.moe/List/ip/china_ip.conf",
)
rules = load_rules(sources, allow={"IP-CIDR", "IP-CIDR6", "IP-ASN"})
write_rules(
    "china_ip.list",
    "Mainland China IP Direct",
    sources,
    rules,
    ("Place near the end of the rule section after all domain rules.",),
    "AGPL-3.0 and CC-BY-SA-2.0",
)
