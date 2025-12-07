import requests
urls = [
"https://ruleset.skk.moe/List/ip/domestic.conf",
"https://ruleset.skk.moe/List/ip/china_ip.conf",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)


with open("./Surge/ChinaIP.list", "w") as f:
    f.write("\n".join(result))