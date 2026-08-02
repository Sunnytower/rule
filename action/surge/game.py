from _common import load_rules, remove_values, rule_value, unique, write_rules


steam_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Steam/Steam.list"
steam_cn_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/SteamCN/SteamCN.list"
playstation_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/PlayStation/PlayStation.list"
nintendo_source = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Nintendo/Nintendo.list"

steam_cn = load_rules((steam_cn_source,), allow={"DOMAIN", "DOMAIN-SUFFIX"})
steam_cn_values = {rule.split(",", 2)[1].lower() for rule in steam_cn}
steam = load_rules((steam_source,), allow={"DOMAIN", "DOMAIN-SUFFIX"})
steam = [rule for rule in steam if not rule_value(rule).endswith(".steamchina.com")]
steam = remove_values(
    steam,
    steam_cn_values
    | {
        "fanatical.com",
        "humblebundle.com",
        "playartifact.com",
        "steamstat.us",
        "steamunlocked.net",
        "underlords.com",
        "steampowered.com",
    },
)
steam.extend(
    [
        "DOMAIN,store.steampowered.com",
        "DOMAIN,help.steampowered.com",
        "DOMAIN,api.steampowered.com",
    ]
)
playstation = load_rules((playstation_source,), allow={"DOMAIN", "DOMAIN-SUFFIX"})
nintendo = [
    "DOMAIN-SUFFIX,nintendo-europe-sales.com",
    "DOMAIN-SUFFIX,nintendo-europe.com",
    "DOMAIN-SUFFIX,nintendo.at",
    "DOMAIN-SUFFIX,nintendo.be",
    "DOMAIN-SUFFIX,nintendo.ch",
    "DOMAIN-SUFFIX,nintendo.co.jp",
    "DOMAIN-SUFFIX,nintendo.co.kr",
    "DOMAIN-SUFFIX,nintendo.co.uk",
    "DOMAIN-SUFFIX,nintendo.co.za",
    "DOMAIN-SUFFIX,nintendo.com",
    "DOMAIN-SUFFIX,nintendo.com.au",
    "DOMAIN-SUFFIX,nintendo.com.hk",
    "DOMAIN-SUFFIX,nintendo.com.pt",
    "DOMAIN-SUFFIX,nintendo.de",
    "DOMAIN-SUFFIX,nintendo.dk",
    "DOMAIN-SUFFIX,nintendo.es",
    "DOMAIN-SUFFIX,nintendo.eu",
    "DOMAIN-SUFFIX,nintendo.fi",
    "DOMAIN-SUFFIX,nintendo.fr",
    "DOMAIN-SUFFIX,nintendo.it",
    "DOMAIN-SUFFIX,nintendo.jp",
    "DOMAIN-SUFFIX,nintendo.net",
    "DOMAIN-SUFFIX,nintendo.nl",
    "DOMAIN-SUFFIX,nintendo.no",
    "DOMAIN-SUFFIX,nintendo.pt",
    "DOMAIN-SUFFIX,nintendo.se",
    "DOMAIN-SUFFIX,nintendo.tw",
    "DOMAIN-SUFFIX,nintendoeurope.com",
    "DOMAIN-SUFFIX,nintendonetwork.net",
    "DOMAIN-SUFFIX,nintendostore.com",
    "DOMAIN-SUFFIX,nintendoswitch.com",
    "DOMAIN-SUFFIX,nintendoswitch.net",
    "DOMAIN-SUFFIX,nintendowifi.net",
    "DOMAIN-SUFFIX,playnintendo.com",
]
rules = unique([*steam, *playstation, *nintendo])
write_rules(
    "game.list",
    "Steam PlayStation Nintendo Core",
    (steam_source, steam_cn_source, playstation_source, nintendo_source),
    rules,
    (
        "Steam China download hosts are excluded because game_download.list must match first.",
        "Nintendo is limited to platform, account, store and network domains; title sites and 35.192.0.0/12 are excluded.",
    ),
    "GPL-2.0",
)
