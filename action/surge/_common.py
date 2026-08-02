from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "surge"
MARKER = "7h15_ru1353t_1s_m4d3_by_5ukk4w.skk.moe"


def fetch(url):
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Sunnytower-rule"},
    )
    response.raise_for_status()
    text = response.content.decode("utf-8-sig")
    if not text.strip():
        raise RuntimeError(f"empty response: {url}")
    return text


def unique(items):
    result = []
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def load_rules(urls, allow=None, deny=None):
    result = []
    for url in urls:
        for raw in fetch(url).splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or MARKER in line or "," not in line:
                continue
            kind, value = line.split(",", 1)
            kind = kind.strip().upper()
            if allow and kind not in allow:
                continue
            if deny and kind in deny:
                continue
            result.append(f"{kind},{value.strip()}")
    return unique(result)


def load_domainset(url):
    result = []
    for raw in fetch(url).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or MARKER in line:
            continue
        if "," in line:
            raise RuntimeError(f"invalid DOMAIN-SET entry: {line}")
        result.append(line)
    return unique(result)


def rule_value(rule):
    parts = rule.split(",")
    return parts[1].strip().lower() if len(parts) > 1 else ""


def remove_values(rules, values):
    values = {value.lower() for value in values}
    return [rule for rule in rules if rule_value(rule) not in values]


def write_rules(filename, name, sources, rules, notes=(), license_name=None):
    rules = unique(rules)
    if not rules:
        raise RuntimeError(f"no rules generated for {filename}")
    lines = [f"# NAME: {name}"]
    lines.extend(f"# SOURCE: {source}" for source in sources)
    if license_name:
        lines.append(f"# LICENSE: {license_name}")
    lines.extend(f"# NOTE: {note}" for note in notes)
    lines.extend([f"# TOTAL: {len(rules)}", "", *rules, ""])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / filename).write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_domainset(filename, name, source, rules, notes=(), license_name=None):
    write_rules(filename, name, (source,), rules, notes, license_name)
