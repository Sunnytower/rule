from _common import write_rules


rules = [
    "DOMAIN,captive.apple.com",
    "DOMAIN,api.smoot.apple.com",
    "DOMAIN,api.smoot.apple.cn",
    "DOMAIN,gs-loc.apple.com",
    "DOMAIN,gs-loc-cn.apple.com",
    "DOMAIN-SUFFIX,ls.apple.com",
    "DOMAIN-SUFFIX,lcdn-locator.apple.com",
    "DOMAIN-SUFFIX,lcdn-registration.apple.com",
    "DOMAIN-SUFFIX,apple-mapkit.com",
    "DOMAIN-SUFFIX,maps.apple.com",
    "DOMAIN-SUFFIX,weather.apple.com",
    "DOMAIN-SUFFIX,weather-data.apple.com",
    "DOMAIN-SUFFIX,weatherkit.apple.com",
    "DOMAIN-SUFFIX,weather-map.apple.com",
    "DOMAIN-SUFFIX,weather-map2.apple.com",
    "PROCESS-NAME,com.apple.geod",
    "PROCESS-NAME,mapspushd",
    "PROCESS-NAME,com.apple.Maps",
    "PROCESS-NAME,CoreLocationAgent",
    "PROCESS-NAME,WeatherWidget",
]
write_rules(
    "apple_direct.list",
    "Apple Maps Weather Location Direct",
    (),
    rules,
    ("Keep ai.list before this ruleset.",),
)
