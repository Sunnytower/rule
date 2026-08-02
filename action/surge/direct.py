from _common import load_rules, remove_values, write_rules


sources = ("https://ruleset.skk.moe/List/non_ip/domestic.conf",)
rules = load_rules(
    sources,
    deny={"URL-REGEX", "IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
rules = remove_values(
    rules,
    {
        "battle.net",
        "blizzard.com",
        "cm.steampowered.com",
        "klook.com",
        "steam.clngaa.com",
        "steam.ksyna.com",
        "steamchina.com",
        "steamcontent.com",
        "steamserver.net",
        "steamusercontent.com",
    },
)
write_rules(
    "direct.list",
    "Mainland China Domestic Direct",
    sources,
    rules,
    ("Sukka direct.conf is not merged; generic Steam CDN suffixes are left to the later China IP rule.",),
    "AGPL-3.0",
)
