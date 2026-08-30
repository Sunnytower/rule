#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "surge"
DST = ROOT / "sing-box"

FILES = [
    "ai.list",
    "apple.list",
    "apple_cdn.list",
    "china_ip.list",
    "direct.list",
    "game.list",
    "game_download.list",
    "global.list",
    "microsoft.list",
]

# Surge DOMAIN-SET，不是普通 RULE-SET
DOMAIN_SET_FILES = {
    "apple_cdn.list",
}

TYPE_MAP = {
    "DOMAIN": "domain",
    "DOMAIN-SUFFIX": "domain_suffix",
    "DOMAIN-KEYWORD": "domain_keyword",
    "IP-CIDR": "ip_cidr",
    "IP-CIDR6": "ip_cidr",
}

# 在家庭网关上无法等价转换
INTENTIONALLY_UNSUPPORTED = {
    "PROCESS-NAME",
    "PROCESS-PATH",
    "URL-REGEX",
}


def unique(values):
    return list(dict.fromkeys(values))


def convert_domain_set(path: Path):
    exact = []
    suffix = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("."):
            # sing-box 1.9+ 推荐不带 "."，
            # 这样同时匹配根域名和子域名。
            suffix.append(line[1:])
        else:
            exact.append(line)

    rules = []

    if exact:
        rules.append({"domain": unique(exact)})

    if suffix:
        rules.append({"domain_suffix": unique(suffix)})

    return rules


def convert_rule_set(path: Path):
    buckets = defaultdict(list)

    for lineno, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        parts = [part.strip() for part in line.split(",")]

        if len(parts) < 2:
            raise RuntimeError(
                f"{path}:{lineno}: unknown line: {line}"
            )

        rule_type = parts[0].upper()
        value = parts[1]

        if rule_type in TYPE_MAP:
            buckets[TYPE_MAP[rule_type]].append(value)
            continue

        if rule_type in INTENTIONALLY_UNSUPPORTED:
            print(
                f"WARN: skip {path.name}:{lineno}: "
                f"{rule_type},{value}",
                file=sys.stderr,
            )
            continue

        # 遇到未来新增但未实现的规则时直接失败，
        # 不允许静默产生错误规则集。
        raise RuntimeError(
            f"{path}:{lineno}: unsupported rule type: {rule_type}"
        )

    # 不把 domain + ip_cidr 混在同一个 headless rule，
    # 避免 AND 语义造成错误匹配。
    rules = []

    for key in (
        "domain",
        "domain_suffix",
        "domain_keyword",
        "ip_cidr",
    ):
        values = unique(buckets[key])

        if values:
            rules.append({
                key: values
            })

    return rules


def main():
    DST.mkdir(parents=True, exist_ok=True)

    for filename in FILES:
        src = SRC / filename

        if filename in DOMAIN_SET_FILES:
            rules = convert_domain_set(src)
        else:
            rules = convert_rule_set(src)

        output = {
            "version": 4,
            "rules": rules,
        }

        target = DST / (
            Path(filename).stem + ".json"
        )

        target.write_text(
            json.dumps(
                output,
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

        print(
            f"{src.relative_to(ROOT)} "
            f"-> {target.relative_to(ROOT)}"
        )


if __name__ == "__main__":
    main()