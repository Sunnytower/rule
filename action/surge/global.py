from _common import load_rules, write_rules


sources = (
    "https://ruleset.skk.moe/List/non_ip/global.conf",
    "https://ruleset.skk.moe/List/non_ip/cdn.conf",
)
rules = load_rules(
    sources,
    deny={"URL-REGEX", "IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
write_rules(
    "global.list",
    "General Global and CDN Proxy",
    sources,
    rules,
    ("download.conf is not merged; unmatched overseas and NSFW traffic remains covered by FINAL,Proxy.",),
    "AGPL-3.0",
)
