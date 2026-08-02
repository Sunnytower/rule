from _common import load_rules, write_rules


sources = ("https://ruleset.skk.moe/List/non_ip/stream.conf",)
rules = load_rules(
    sources,
    deny={"IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
write_rules(
    "media.list",
    "Global Streaming Media",
    sources,
    rules,
    ("Aggregates Netflix, Max, Disney+, YouTube, Twitch, Spotify and other streaming services.",),
    "AGPL-3.0",
)
