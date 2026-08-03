from _common import load_rules, unique, write_rules


sources = (
    "https://ruleset.skk.moe/List/non_ip/microsoft.conf",
)
rules = load_rules(
    sources,
    deny={"URL-REGEX", "IP-CIDR", "IP-CIDR6", "IP-ASN"},
)
rules = unique(
    rules
    + [
        "DOMAIN-SUFFIX,aadrm.cn",
        "DOMAIN-SUFFIX,azure.cn",
        "DOMAIN-SUFFIX,bing.com.cn",
        "DOMAIN-SUFFIX,biying.cn",
        "DOMAIN-SUFFIX,biying.com.cn",
        "DOMAIN-SUFFIX,chinacloudapi.cn",
        "DOMAIN-SUFFIX,chinacloudapp.cn",
        "DOMAIN-SUFFIX,chinacloudsites.cn",
        "DOMAIN-SUFFIX,live.cn",
        "DOMAIN-SUFFIX,lync.cn",
        "DOMAIN-SUFFIX,microsoft-online.cn",
        "DOMAIN-SUFFIX,microsoftonline.cn",
        "DOMAIN-SUFFIX,msappproxy.cn",
        "DOMAIN-SUFFIX,msauth.cn",
        "DOMAIN-SUFFIX,msauthimages.cn",
        "DOMAIN-SUFFIX,msftauth.cn",
        "DOMAIN-SUFFIX,msftauthimages.cn",
        "DOMAIN-SUFFIX,msidentity.cn",
        "DOMAIN-SUFFIX,msn.cn",
        "DOMAIN-SUFFIX,office365.cn",
        "DOMAIN-SUFFIX,officewebapps.cn",
        "DOMAIN-SUFFIX,onmschina.cn",
        "DOMAIN-SUFFIX,outlook.cn",
        "DOMAIN-SUFFIX,powerapps.cn",
        "DOMAIN-SUFFIX,powerbi.cn",
        "DOMAIN-SUFFIX,sharepoint.cn",
        "DOMAIN-SUFFIX,xboxlive.cn",
    ]
)
write_rules(
    "microsoft.list",
    "Microsoft Default Proxy",
    sources,
    rules,
    ("Includes Microsoft mainland CDN and a compact set of common China endpoints.",),
    "AGPL-3.0",
)
