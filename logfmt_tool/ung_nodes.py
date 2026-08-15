"""UNG adapter registry for logfmt-tool (see nodepacker's ADAPTER_SPEC.md).

Pure JSON-in/JSON-out wrappers over :mod:`logfmt_tool.core` for parsing,
serializing, filtering, projecting, and profiling logfmt records.
"""

from __future__ import annotations

from logfmt_tool.core import (
    compute_stats,
    filter_records,
    parse,
    select,
    to_logfmt,
)


def parse_logfmt(text: str) -> list[dict]:
    """Parse logfmt lines into records; bare keys become true flags."""
    return parse(text)


def format_logfmt(records: list[dict]) -> str:
    """Serialize records to logfmt lines, quoting values only when needed."""
    return "\n".join(to_logfmt(record) for record in records)


def filter_logfmt_records(records: list[dict], expression: str) -> list[dict]:
    """Keep records matching one key=value / comparison / existence expression."""
    return filter_records(records, expression)


def select_keys(records: list[dict], keys: list[str]) -> list[dict]:
    """Project each record onto the requested keys, keeping only present ones."""
    return [select(record, keys) for record in records]


def profile_records(records: list[dict], top: int = 5) -> dict:
    """Profile key presence, distinct counts, and top values across records."""
    return compute_stats(records, top=top)


NODES = [
    {
        "fn": parse_logfmt,
        "id": "amarel.logfmttool.parse-logfmt",
        "capabilities": ["logs.parse-logfmt"],
        "summary": "Parse logfmt key=value log lines into structured records.",
        "inputs": [
            {"name": "text", "type_id": "amarel.text",
             "description": "Raw log text, one logfmt line per record."}
        ],
        "outputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Parsed records; bare keys become true flags."}
        ],
        "parameters": [],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
        "postconditions": ["blank lines are skipped; duplicate keys keep the last value"],
    },
    {
        "fn": format_logfmt,
        "id": "amarel.logfmttool.format-logfmt",
        "capabilities": ["logs.format-logfmt"],
        "summary": "Serialize structured records back to logfmt lines.",
        "inputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Records to serialize, key order preserved."}
        ],
        "outputs": [
            {"name": "text", "type_id": "amarel.text",
             "description": "One logfmt line per record."}
        ],
        "parameters": [],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
    {
        "fn": filter_logfmt_records,
        "id": "amarel.logfmttool.filter-records",
        "capabilities": ["logs.filter-records"],
        "summary": (
            "Keep records matching one transparent key=value, comparison, or "
            "existence expression."
        ),
        "inputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Records to filter."}
        ],
        "outputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Records satisfying the expression."}
        ],
        "parameters": [
            {"name": "expression", "value_type": "string", "default": None,
             "required": True,
             "description": "Filter like level=error, status>=500, or bare key."}
        ],
        "candidates": [
            {"name": "level-error", "parameters": {"expression": "level=error"}},
            {"name": "status-ge-500", "parameters": {"expression": "status>=500"}},
        ],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
    {
        "fn": select_keys,
        "id": "amarel.logfmttool.select-keys",
        "capabilities": ["logs.project-keys"],
        "summary": "Project each record onto an explicit key list.",
        "inputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Records to project."}
        ],
        "outputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Projected records; absent keys are simply omitted."}
        ],
        "parameters": [
            {"name": "keys", "value_type": "array[string]", "default": None,
             "required": True, "description": "Keys to keep, in output order."}
        ],
        "candidates": [
            {"name": "level-msg", "parameters": {"keys": ["level", "msg"]}},
            {"name": "timing", "parameters": {"keys": ["ts", "elapsed_ms"]}},
        ],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
    {
        "fn": profile_records,
        "id": "amarel.logfmttool.profile-records",
        "capabilities": ["logs.profile-records"],
        "summary": "Profile key presence, distinct counts, and top values across records.",
        "inputs": [
            {"name": "records", "type_id": "amarel.records",
             "description": "Records to profile."}
        ],
        "outputs": [
            {"name": "report", "type_id": "amarel.report",
             "description": "Per-key presence, percentage, distinct, and top values."}
        ],
        "parameters": [
            {"name": "top", "value_type": "integer", "default": 5,
             "required": False, "choices": [3, 5],
             "description": "How many most-common values to report per key."}
        ],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
]
