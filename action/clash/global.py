import os
import requests
urls = [
# "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Global/Global.list",
"https://ruleset.skk.moe/Clash/non_ip/cdn.txt",
"https://ruleset.skk.moe/Clash/non_ip/global.txt",
"https://ruleset.skk.moe/Clash/non_ip/download.txt",
"https://ruleset.skk.moe/Clash/non_ip/telegram.txt",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)

file_path = "./clash/global.txt"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    f.write("\n".join(result))
