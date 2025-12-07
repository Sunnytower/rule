import requests
urls = [
"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/ChinaASN/ChinaASN.list",
]
result = []
for url in urls:
    resource_text = requests.get(url).text
    for item in resource_text.split("\n"):
        if (item not in result) and (not item.startswith('#')):
            result.append(item)


with open("./Surge/ChinaASN.list", "w") as f:
    f.write("\n".join(result))
