import requests
urls = [
"https://ruleset.skk.moe/List/non_ip/domestic.conf",
"https://ruleset.skk.moe/List/non_ip/direct.conf",
]
result = ["DOMAIN-SUFFIX,ctest.srv.nintendo.net"]
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)


with open("./Surge/Direct.list", "w") as f:
    f.write("\n".join(result))
