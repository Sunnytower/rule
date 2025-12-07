import requests
urls = [
"https://ruleset.skk.moe/Clash/non_ip/domestic.txt",
"https://ruleset.skk.moe/Clash/non_ip/direct.txt",
#"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BiliBili/BiliBili.list",
#"https://raw.githubusercontent.com/Blankwonder/surge-list/master/cn.list",
#"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/SteamCN/SteamCN.list",
# "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Xbox/Xbox.list",
# "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Epic/Epic.list",
# "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/EA/EA.list",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#') and (not item.startswith("USER-AGENT"))):
            result.append(item)


with open("./Clash/Direct.txt", "w") as f:
    f.write("\n".join(result))
