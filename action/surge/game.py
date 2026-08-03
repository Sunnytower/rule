from _common import load_rules, remove_values, unique, write_rules

steam_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Steam/Steam.list"
playstation_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/PlayStation/PlayStation.list"
nintendo_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Nintendo/Nintendo.list"

steam = load_rules(
    (steam_source,),
    allow={"DOMAIN", "DOMAIN-SUFFIX"},
)

steam = remove_values(
    steam,
    {
        "fanatical.com",
        "humblebundle.com",
        "playartifact.com",
        "steamstat.us",
        "steamunlocked.net",
        "underlords.com",
    },
)

playstation = load_rules(
    (playstation_source,),
    allow={"DOMAIN", "DOMAIN-SUFFIX"},
)

nintendo = [
    "DOMAIN-SUFFIX,nintendo.com",
    "DOMAIN-SUFFIX,nintendo.net",
    "DOMAIN-SUFFIX,nintendonetwork.net",
    "DOMAIN-SUFFIX,nintendostore.com",
    "DOMAIN-SUFFIX,nintendoswitch.com",
    "DOMAIN-SUFFIX,nintendoswitch.net",
    "DOMAIN-SUFFIX,nintendowifi.net",
]

rules = unique([*steam, *playstation, *nintendo])

write_rules(
    "game.list",
    "Steam PlayStation Nintendo",
    (steam_source, playstation_source),
    rules,
    ("Nintendo keeps only core platform, account, store and network domains.",),
    "GPL-2.0",
)