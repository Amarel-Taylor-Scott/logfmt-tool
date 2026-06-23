"""Parse, query, and emit logfmt — the ``key=value`` structured-log format. Pure stdlib.

logfmt (popularized by Heroku and Go's go-kit) encodes a log line as space-separated
``key=value`` pairs, values optionally double-quoted:

    level=info msg="user logged in" user_id=42 ok elapsed_ms=12.5

This module parses such lines into dicts, serializes dicts back to logfmt, and
provides small filter / select / stats helpers for log triage on the command line.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict


def parse_line(line: str) -> dict:
    """Parse one logfmt line into a dict.

    - ``key=value`` -> ``{"key": "value"}``
    - ``key="a b"`` -> quoted values may contain spaces; ``\\"`` and ``\\\\`` escape
    - ``key=``      -> empty string
    - bare ``key``  -> ``True`` (a present flag)
    - duplicate keys -> last one wins
    """
    result: dict = {}
    i, n = 0, len(line)
    while i < n:
        while i < n and line[i] == " ":
            i += 1
        if i >= n:
            break
        # read key (up to '=' or space)
        start = i
        while i < n and line[i] not in "= ":
            i += 1
        key = line[start:i]
        if i < n and line[i] == "=":
            i += 1
            if i < n and line[i] == '"':
                i += 1
                buf = []
                while i < n and line[i] != '"':
                    if line[i] == "\\" and i + 1 < n:
                        i += 1
                    buf.append(line[i])
                    i += 1
                i += 1  # closing quote
                value = "".join(buf)
            else:
                vstart = i
                while i < n and line[i] != " ":
                    i += 1
                value = line[vstart:i]
            if key:
                result[key] = value
        else:
            if key:
                result[key] = True
    return result


def parse(text: str) -> list[dict]:
    return [parse_line(line) for line in text.splitlines() if line.strip()]


_NEEDS_QUOTING = re.compile(r'[ =":]')


def _quote(value: str) -> str:
    if value == "" or _NEEDS_QUOTING.search(value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def to_logfmt(record: dict) -> str:
    """Serialize a dict to a logfmt line (insertion order preserved)."""
    parts = []
    for key, value in record.items():
        if value is True:
            parts.append(f"{key}=true")
        elif value is False:
            parts.append(f"{key}=false")
        else:
            parts.append(f"{key}={_quote(str(value))}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
_OPS = ["!=", ">=", "<=", "=", ">", "<"]


def parse_filter(expr: str):
    """Parse a filter like 'level=error', 'status>=500', or bare 'err' (key exists)."""
    for op in _OPS:
        idx = expr.find(op)
        if idx > 0:
            return expr[:idx], op, expr[idx + len(op):]
    return expr, "exists", None


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def match(record: dict, key: str, op: str, value) -> bool:
    if key not in record:
        return False
    if op == "exists":
        return True
    actual = record[key]
    if op in ("=", "!="):
        eq = str(actual) == str(value)
        return eq if op == "=" else not eq
    a, b = _num(actual), _num(value)
    if a is None or b is None:
        return False
    return {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b}[op]


def filter_records(records: list[dict], expr: str) -> list[dict]:
    key, op, value = parse_filter(expr)
    return [r for r in records if match(r, key, op, value)]


def select(record: dict, keys: list[str]) -> dict:
    return {k: record[k] for k in keys if k in record}


def compute_stats(records: list[dict], *, top: int = 5) -> dict:
    n = len(records)
    present: Counter = Counter()
    values: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        for k, v in r.items():
            present[k] += 1
            values[k][str(v)] += 1
    out = {"records": n, "keys": {}}
    for k in sorted(present):
        out["keys"][k] = {
            "present": present[k],
            "present_pct": round(100 * present[k] / n, 1) if n else 0.0,
            "distinct": len(values[k]),
            "top": values[k].most_common(top),
        }
    return out
