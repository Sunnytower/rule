from _common import load_rules, remove_values, write_rules


sources = (
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/SteamCN/SteamCN.list",
)
rules = load_rules(sources, allow={"DOMAIN", "DOMAIN-SUFFIX"})
rules = remove_values(
    rules,
    {
        "cm.steampowered.com",
        "steamcontent.com",
        "steamserver.net",
        "steamusercontent.com",
    },
)
write_rules(
    "game_download.list",
    "Steam China Download Direct",
    sources,
    rules,
    ("Generic Steam CDN suffixes are excluded and classified by the later China IP rule.",),
    "GPL-2.0",
)
