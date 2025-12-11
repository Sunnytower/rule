import os
import requests
urls = [
"https://ruleset.skk.moe/Clash/non_ip/telegram.txt",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)

file_path = "./clash/telegram.txt"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    f.write("\n".join(result))