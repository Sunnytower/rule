#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import io
import ipaddress
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "rulesets.yaml"
TARGETS = ("surge", "sing-box", "mihomo")
SOURCE_FORMATS = ("surge", "sing-box", "mihomo")
SINGBOX_FIELDS = (
    "domain",
    "domain_suffix",
    "domain_keyword",
    "domain_regex",
    "ip_cidr",
)
SINGBOX_TYPE_MAP = {
    "domain": "domain",
    "domain_suffix": "domain_suffix",
    "domain_keyword": "domain_keyword",
    "domain_regex": "domain_regex",
    "ip_cidr": "ip_cidr",
    "ip_cidr6": "ip_cidr",
}
MIHOMO_KINDS = {
    "domain",
    "domain_suffix",
    "domain_keyword",
    "domain_wildcard",
    "domain_regex",
    "ip_cidr",
    "ip_cidr6",
    "process_name",
    "process_name_wildcard",
    "process_name_regex",
    "process_path",
    "process_path_wildcard",
    "process_path_regex",
}
MIHOMO_OMIT_KINDS = {"user_agent", "url_regex"}
MIHOMO_REGEX_KINDS = {
    "domain_regex",
    "process_name_regex",
    "process_path_regex",
}


class BuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class Rule:
    kind: str
    value: str
    options: Tuple[str, ...] = ()
    raw_surge: Optional[str] = field(default=None, compare=False)
    native_mihomo: bool = field(default=False, compare=False)
    origin: str = field(default="", compare=False)


@dataclass(frozen=True)
class Source:
    url: str
    source_format: str
    targets: Tuple[str, ...]


@dataclass(frozen=True)
class CustomRule:
    rule: Rule
    targets: Tuple[str, ...]
    options_specified: bool = False


@dataclass(frozen=True)
class RuleSet:
    name: str
    sources: Tuple[Source, ...]
    additions: Tuple[CustomRule, ...]
    removals: Tuple[CustomRule, ...]
    targets: Tuple[str, ...]


def normalize_kind(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def parse_targets(value: object, context: str, default: Sequence[str] = ()) -> Tuple[str, ...]:
    if value is None:
        values = list(default)
    elif isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        raise BuildError(f"{context}: targets must be a string or list")

    result: List[str] = []
    for item in values:
        if not isinstance(item, str) or item not in TARGETS:
            raise BuildError(f"{context}: unsupported target {item!r}")
        if item not in result:
            result.append(item)

    if not result:
        raise BuildError(f"{context}: targets cannot be empty")
    return tuple(result)


def parse_options(value: object, context: str) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        raise BuildError(f"{context}: options must be a string or list")

    result: List[str] = []
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise BuildError(f"{context}: every option must be a non-empty string")
        result.append(item.strip())
    return tuple(result)


def parse_custom_rules(
    value: object,
    context: str,
    default_targets: Sequence[str],
) -> Tuple[CustomRule, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise BuildError(f"{context}: must be a list")

    result: List[CustomRule] = []
    for index, item in enumerate(value, 1):
        item_context = f"{context}[{index}]"
        if not isinstance(item, Mapping):
            raise BuildError(f"{item_context}: must be an object")

        kind = item.get("type")
        if not isinstance(kind, str) or not kind.strip():
            raise BuildError(f"{item_context}: type must be a non-empty string")

        has_value = "value" in item
        has_values = "values" in item
        if has_value == has_values:
            raise BuildError(
                f"{item_context}: exactly one of value or values must be provided"
            )
        if has_value:
            raw_values = [item.get("value")]
        else:
            raw_values = item.get("values")
            if not isinstance(raw_values, list) or not raw_values:
                raise BuildError(f"{item_context}: values must be a non-empty list")

        rule_values: List[Tuple[str, str]] = []
        for value_index, rule_value in enumerate(raw_values, 1):
            value_context = (
                item_context if has_value else f"{item_context}.values[{value_index}]"
            )
            if not isinstance(rule_value, str) or not rule_value.strip():
                raise BuildError(f"{value_context}: must be a non-empty string")
            rule_values.append((rule_value.strip(), value_context))

        options_specified = "options" in item
        options = parse_options(item.get("options"), item_context)
        targets = parse_targets(item.get("targets"), item_context, default_targets)
        for rule_value, value_context in rule_values:
            result.append(
                CustomRule(
                    rule=Rule(
                        kind=normalize_kind(kind),
                        value=rule_value,
                        options=options,
                        origin=value_context,
                    ),
                    targets=targets,
                    options_specified=options_specified,
                )
            )
    return tuple(result)


def load_config(path: Path) -> Tuple[RuleSet, ...]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BuildError(f"cannot parse {path}: {exc}") from exc

    if not isinstance(document, Mapping):
        raise BuildError(f"{path}: root must be an object")
    raw_rulesets = document.get("rulesets")
    if not isinstance(raw_rulesets, Mapping) or not raw_rulesets:
        raise BuildError(f"{path}: rulesets must be a non-empty object")

    result: List[RuleSet] = []
    for name, body in raw_rulesets.items():
        context = f"rulesets.{name}"
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise BuildError(f"{context}: invalid ruleset name")
        if not isinstance(body, Mapping):
            raise BuildError(f"{context}: must be an object")

        raw_sources = body.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise BuildError(f"{context}.sources: must be a non-empty list")

        sources: List[Source] = []
        target_order: List[str] = []
        for index, raw_source in enumerate(raw_sources, 1):
            source_context = f"{context}.sources[{index}]"
            if not isinstance(raw_source, Mapping):
                raise BuildError(f"{source_context}: must be an object")

            url = raw_source.get("url")
            source_format = raw_source.get("format")
            if not isinstance(url, str) or not url.strip():
                raise BuildError(f"{source_context}: url must be a non-empty string")
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
                raise BuildError(f"{source_context}: unsupported URL {url!r}")
            if source_format not in SOURCE_FORMATS:
                raise BuildError(f"{source_context}: unsupported format {source_format!r}")

            targets = parse_targets(raw_source.get("targets"), source_context)
            for target in targets:
                if target not in target_order:
                    target_order.append(target)
            sources.append(Source(url.strip(), source_format, targets))

        raw_custom = body.get("custom", {})
        if raw_custom is None:
            raw_custom = {}
        if not isinstance(raw_custom, Mapping):
            raise BuildError(f"{context}.custom: must be an object")

        additions = parse_custom_rules(
            raw_custom.get("add"),
            f"{context}.custom.add",
            target_order,
        )
        removals = parse_custom_rules(
            raw_custom.get("remove"),
            f"{context}.custom.remove",
            target_order,
        )
        for custom_rule in additions + removals:
            for target in custom_rule.targets:
                if target not in target_order:
                    target_order.append(target)

        result.append(
            RuleSet(
                name=name,
                sources=tuple(sources),
                additions=additions,
                removals=removals,
                targets=tuple(target_order),
            )
        )

    return tuple(result)


def fetch_url(url: str) -> str:
    request = Request(
        url,
        headers={
            "Accept": "application/json, text/plain;q=0.9, */*;q=0.1",
            "User-Agent": "Sunnytower-rule-builder/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            status = response.getcode()
            if status != 200:
                raise BuildError(f"download failed: {url}: HTTP {status}")
            payload = response.read()
    except HTTPError as exc:
        raise BuildError(f"download failed: {url}: HTTP {exc.code}") from exc
    except (URLError, OSError) as exc:
        raise BuildError(f"download failed: {url}: {exc}") from exc

    if not payload.strip():
        raise BuildError(f"download failed: {url}: empty response")
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise BuildError(f"download failed: {url}: response is not UTF-8") from exc


def download_sources(rulesets: Sequence[RuleSet]) -> Dict[str, str]:
    downloaded: Dict[str, str] = {}
    for ruleset in rulesets:
        for source in ruleset.sources:
            if source.url in downloaded:
                continue
            print(f"fetch {source.url}")
            downloaded[source.url] = fetch_url(source.url)
    return downloaded


def parse_surge(text: str, origin: str) -> Tuple[Rule, ...]:
    result: List[Rule] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        try:
            fields = next(csv.reader([line], skipinitialspace=True, strict=True))
        except csv.Error as exc:
            raise BuildError(f"{origin}:{line_number}: invalid Surge rule: {exc}") from exc
        fields = [item.strip() for item in fields]
        if len(fields) < 2:
            raise BuildError(f"{origin}:{line_number}: invalid Surge rule: {line}")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", fields[0]):
            raise BuildError(f"{origin}:{line_number}: invalid rule type {fields[0]!r}")
        if not fields[1]:
            raise BuildError(f"{origin}:{line_number}: rule value cannot be empty")

        result.append(
            Rule(
                kind=normalize_kind(fields[0]),
                value=fields[1],
                options=tuple(item for item in fields[2:] if item),
                raw_surge=line,
                origin=f"{origin}:{line_number}",
            )
        )

    if not result:
        raise BuildError(f"{origin}: no rules found")
    return tuple(result)


def parse_singbox(text: str, origin: str) -> Tuple[Rule, ...]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BuildError(f"{origin}: invalid sing-box JSON: {exc}") from exc

    if not isinstance(document, Mapping):
        raise BuildError(f"{origin}: sing-box root must be an object")
    if not isinstance(document.get("version"), int) or document["version"] < 1:
        raise BuildError(f"{origin}: invalid sing-box version")
    raw_rules = document.get("rules")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise BuildError(f"{origin}: sing-box rules must be a non-empty list")

    result: List[Rule] = []
    for rule_index, raw_rule in enumerate(raw_rules, 1):
        rule_context = f"{origin}:rules[{rule_index}]"
        if not isinstance(raw_rule, Mapping) or not raw_rule:
            raise BuildError(f"{rule_context}: must be a non-empty object")
        for field_name, raw_values in raw_rule.items():
            if field_name not in SINGBOX_FIELDS:
                raise BuildError(f"{rule_context}: unsupported field {field_name!r}")
            if isinstance(raw_values, str):
                values = [raw_values]
            elif isinstance(raw_values, list):
                values = raw_values
            else:
                raise BuildError(f"{rule_context}.{field_name}: must be a string or list")
            if not values:
                raise BuildError(f"{rule_context}.{field_name}: cannot be empty")
            for value_index, value in enumerate(values, 1):
                if not isinstance(value, str) or not value.strip():
                    raise BuildError(
                        f"{rule_context}.{field_name}[{value_index}]: "
                        "must be a non-empty string"
                    )
                result.append(
                    Rule(
                        kind=field_name,
                        value=value.strip(),
                        origin=f"{rule_context}.{field_name}[{value_index}]",
                    )
                )

    if not result:
        raise BuildError(f"{origin}: no supported rules found")
    return tuple(result)


def parse_mihomo_rule(payload: str, origin: str) -> Rule:
    fields = [item.strip() for item in payload.split(",")]
    if len(fields) < 2:
        raise BuildError(f"{origin}: invalid Mihomo rule: {payload}")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", fields[0]):
        raise BuildError(f"{origin}: invalid rule type {fields[0]!r}")

    kind = normalize_kind(fields[0])
    if kind in MIHOMO_REGEX_KINDS:
        value = ",".join(fields[1:]).strip()
        options: Tuple[str, ...] = ()
    else:
        value = fields[1]
        options = tuple(item for item in fields[2:] if item)
    if not value:
        raise BuildError(f"{origin}: rule value cannot be empty")

    rule = Rule(
        kind=kind,
        value=value,
        options=options,
        native_mihomo=True,
        origin=origin,
    )
    mihomo_parts(rule)
    return rule


def parse_mihomo(text: str, origin: str) -> Tuple[Rule, ...]:
    result: List[Rule] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        item_origin = f"{origin}:{line_number}"
        if "," in line:
            result.append(parse_mihomo_rule(line, item_origin))
            continue
        try:
            network = ipaddress.ip_network(line, strict=False)
        except ValueError as exc:
            raise BuildError(f"{item_origin}: invalid Mihomo rule {line!r}") from exc
        result.append(
            Rule(
                kind="ip_cidr6" if network.version == 6 else "ip_cidr",
                value=line,
                native_mihomo=True,
                origin=item_origin,
            )
        )

    if not result:
        raise BuildError(f"{origin}: no rules found")
    return tuple(result)


def parse_downloads(
    rulesets: Sequence[RuleSet],
    downloaded: Mapping[str, str],
) -> Dict[Tuple[str, str], Tuple[Rule, ...]]:
    parsed: Dict[Tuple[str, str], Tuple[Rule, ...]] = {}
    for ruleset in rulesets:
        for source in ruleset.sources:
            key = (source.url, source.source_format)
            if key in parsed:
                continue
            text = downloaded[source.url]
            if source.source_format == "surge":
                parsed[key] = parse_surge(text, source.url)
            elif source.source_format == "sing-box":
                parsed[key] = parse_singbox(text, source.url)
            elif source.source_format == "mihomo":
                parsed[key] = parse_mihomo(text, source.url)
            else:
                raise AssertionError(f"unhandled source format: {source.source_format}")
    return parsed


def singbox_field(rule: Rule) -> str:
    field_name = SINGBOX_TYPE_MAP.get(rule.kind)
    if field_name is None:
        raise BuildError(
            f"{rule.origin}: {rule.kind.replace('_', '-').upper()} "
            "cannot be converted to sing-box"
        )
    if rule.options:
        normalized_options = {item.lower() for item in rule.options}
        if field_name != "ip_cidr" or normalized_options != {"no-resolve"}:
            raise BuildError(
                f"{rule.origin}: options {rule.options!r} cannot be converted to sing-box"
            )
    return field_name


def surge_type(rule: Rule) -> str:
    if rule.kind == "ip_cidr6":
        return "IP-CIDR6"
    if rule.kind == "ip_cidr":
        return "IP-CIDR6" if ":" in rule.value else "IP-CIDR"
    return rule.kind.replace("_", "-").upper()


def mihomo_parts(
    rule: Rule,
    allow_omit: bool = False,
) -> Optional[Tuple[str, str, Tuple[str, ...]]]:
    if rule.kind in MIHOMO_OMIT_KINDS:
        if allow_omit:
            return None
        raise BuildError(
            f"{rule.origin}: {surge_type(rule)} cannot be converted to mihomo"
        )
    if rule.kind not in MIHOMO_KINDS:
        raise BuildError(
            f"{rule.origin}: {surge_type(rule)} cannot be converted to mihomo"
        )

    kind = rule.kind
    value = rule.value
    if kind == "process_name" and not rule.native_mihomo:
        has_wildcard = "*" in value or "?" in value
        if value.startswith("/"):
            if value.endswith("/"):
                kind = "process_path_wildcard"
                value += "*"
            elif has_wildcard:
                kind = "process_path_wildcard"
            else:
                kind = "process_path"
        elif has_wildcard:
            kind = "process_name_wildcard"

    if "\n" in value or "\r" in value:
        raise BuildError(f"{rule.origin}: mihomo rule value cannot contain a newline")
    if "," in value and kind not in MIHOMO_REGEX_KINDS:
        raise BuildError(
            f"{rule.origin}: {surge_type(rule)} value containing a comma "
            "cannot be converted to mihomo"
        )

    options: Tuple[str, ...] = ()
    if rule.options:
        normalized_options = tuple(item.lower() for item in rule.options)
        if kind not in ("ip_cidr", "ip_cidr6") or normalized_options != (
            "no-resolve",
        ):
            raise BuildError(
                f"{rule.origin}: options {rule.options!r} cannot be converted to mihomo"
            )
        options = normalized_options

    if kind == "ip_cidr6":
        output_type = "IP-CIDR6"
    elif kind == "ip_cidr":
        output_type = "IP-CIDR6" if ":" in value else "IP-CIDR"
    else:
        output_type = kind.replace("_", "-").upper()
    return output_type, value, options


def target_key(rule: Rule, target: str) -> Tuple[object, ...]:
    if target == "sing-box":
        return singbox_field(rule), rule.value
    if target == "mihomo":
        parts = mihomo_parts(rule)
        assert parts is not None
        return parts
    return surge_type(rule), rule.value, rule.options


def removal_matches(rule: Rule, removal: CustomRule, target: str) -> bool:
    if target == "sing-box":
        return target_key(rule, target) == target_key(removal.rule, target)
    if target == "mihomo":
        rule_type, rule_value, rule_options = target_key(rule, target)
        remove_type, remove_value, remove_options = target_key(removal.rule, target)
        if rule_type != remove_type or rule_value != remove_value:
            return False
        return not removal.options_specified or rule_options == remove_options
    if surge_type(rule) != surge_type(removal.rule) or rule.value != removal.rule.value:
        return False
    return not removal.options_specified or rule.options == removal.rule.options


def deduplicate(rules: Iterable[Rule], target: str) -> List[Rule]:
    result: List[Rule] = []
    seen = set()
    for rule in rules:
        key = target_key(rule, target)
        if key in seen:
            continue
        seen.add(key)
        result.append(rule)
    return result


def render_surge(rules: Sequence[Rule]) -> str:
    lines: List[str] = []
    for rule in rules:
        if rule.raw_surge is not None:
            lines.append(rule.raw_surge)
            continue
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="")
        writer.writerow([surge_type(rule), rule.value, *rule.options])
        lines.append(output.getvalue())
    return "\n".join(lines) + "\n"


def render_mihomo(rules: Sequence[Rule]) -> str:
    lines: List[str] = []
    for rule in rules:
        parts = mihomo_parts(rule)
        assert parts is not None
        rule_type, value, options = parts
        lines.append(",".join([rule_type, value, *options]))
    return "\n".join(lines) + "\n"


def render_singbox(rules: Sequence[Rule]) -> str:
    buckets: Dict[str, List[str]] = {field_name: [] for field_name in SINGBOX_FIELDS}
    for rule in rules:
        buckets[singbox_field(rule)].append(rule.value)
    rule_object = {
        field_name: values
        for field_name, values in buckets.items()
        if values
    }
    document = {
        "version": 2,
        "rules": [rule_object],
    }
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def build_outputs(
    rulesets: Sequence[RuleSet],
    parsed: Mapping[Tuple[str, str], Tuple[Rule, ...]],
) -> Dict[Path, str]:
    outputs: Dict[Path, str] = {}
    for ruleset in rulesets:
        target_rules: Dict[str, List[Rule]] = {target: [] for target in ruleset.targets}
        mihomo_omitted = 0
        for source in ruleset.sources:
            source_rules = parsed[(source.url, source.source_format)]
            for target in source.targets:
                if target == "sing-box":
                    for rule in source_rules:
                        singbox_field(rule)
                    target_rules[target].extend(source_rules)
                elif target == "mihomo":
                    for rule in source_rules:
                        allow_omit = source.source_format == "surge"
                        if mihomo_parts(rule, allow_omit=allow_omit) is None:
                            mihomo_omitted += 1
                        else:
                            target_rules[target].append(rule)
                else:
                    target_rules[target].extend(source_rules)

        if mihomo_omitted:
            print(
                f"omit mihomo/{ruleset.name}.list "
                f"({mihomo_omitted} unsupported rules)"
            )

        for removal in ruleset.removals:
            for target in removal.targets:
                if target == "mihomo":
                    mihomo_parts(removal.rule)
                target_rules[target] = [
                    rule
                    for rule in target_rules[target]
                    if not removal_matches(rule, removal, target)
                ]

        for addition in ruleset.additions:
            for target in addition.targets:
                if target == "sing-box":
                    singbox_field(addition.rule)
                elif target == "mihomo":
                    mihomo_parts(addition.rule)
                target_rules[target].append(addition.rule)

        for target in ruleset.targets:
            rules = deduplicate(target_rules[target], target)
            if not rules:
                raise BuildError(f"rulesets.{ruleset.name}: {target} output has no rules")
            if target == "surge":
                path = ROOT / "surge" / f"{ruleset.name}.list"
                outputs[path] = render_surge(rules)
            elif target == "sing-box":
                path = ROOT / "sing-box" / f"{ruleset.name}.json"
                outputs[path] = render_singbox(rules)
            else:
                path = ROOT / "mihomo" / f"{ruleset.name}.list"
                outputs[path] = render_mihomo(rules)
            print(f"build {path.relative_to(ROOT)} ({len(rules)} rules)")
    return outputs


def publish(outputs: Mapping[Path, str]) -> int:
    changed = {
        path: content.encode("utf-8")
        for path, content in outputs.items()
        if not path.exists() or path.read_bytes() != content.encode("utf-8")
    }
    if not changed:
        print("no output changes")
        return 0

    with tempfile.TemporaryDirectory(prefix=".rulegen-", dir=ROOT) as temp_name:
        temp_root = Path(temp_name)
        staged: Dict[Path, Path] = {}
        for final_path, payload in changed.items():
            relative_path = final_path.relative_to(ROOT)
            staged_path = temp_root / relative_path
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_bytes(payload)
            staged[final_path] = staged_path

        for final_path, staged_path in staged.items():
            final_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_path, final_path)

    print(f"published {len(changed)} changed files")
    return len(changed)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Surge, sing-box, and mihomo rules"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"ruleset configuration (default: {DEFAULT_CONFIG})",
    )
    args = parser.parse_args(argv)

    try:
        rulesets = load_config(args.config)
        downloaded = download_sources(rulesets)
        parsed = parse_downloads(rulesets, downloaded)
        outputs = build_outputs(rulesets, parsed)
        publish(outputs)
    except (BuildError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
