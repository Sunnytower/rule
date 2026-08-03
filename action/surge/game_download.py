from _common import load_rules, write_rules

sources = (
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/SteamCN/SteamCN.list",
)

rules = load_rules(
    sources,
    allow={"DOMAIN", "DOMAIN-SUFFIX"},
)

write_rules(
    "game_download.list",
    "Steam Direct",
    sources,
    rules,
    (
        "Steam China download, content and related service domains use DIRECT.",
    ),
    "GPL-2.0",
)