from _common import load_domainset, write_domainset


source = "https://ruleset.skk.moe/List/domainset/apple_cdn.conf"
rules = load_domainset(source)
write_domainset(
    "apple_cdn.list",
    "Apple Mainland CDN Default Proxy",
    source,
    rules,
    ("Use as DOMAIN-SET and assign to Apple rather than DIRECT.",),
    "AGPL-3.0",
)
