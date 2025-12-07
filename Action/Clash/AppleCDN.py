import requests
urls = [
"https://ruleset.skk.moe/Clash/domainset/apple_cdn.txt",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)


with open("./Clash/AppleCDN.txt", "w") as f:
    f.write("\n".join(result))
