import os
import requests
urls = [
"https://ruleset.skk.moe/List/domainset/apple_cdn.conf",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)

file_path = "./surge/apple_cdn.list"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    f.write("\n".join(result))
