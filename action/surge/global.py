import os
import requests
urls = [
# "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Proxy/Proxy_All_No_Resolve.list",
"https://ruleset.skk.moe/List/non_ip/cdn.conf",
"https://ruleset.skk.moe/List/non_ip/global.conf",
"https://ruleset.skk.moe/List/non_ip/download.conf",
"https://ruleset.skk.moe/List/non_ip/telegram.conf",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)

file_path = "./surge/global.list"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    f.write("\n".join(result))