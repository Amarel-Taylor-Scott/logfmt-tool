"""Run every UNG adapter fixture case (nodepacker ADAPTER_SPEC.md section 5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from logfmt_tool import ung_nodes

FIXTURES_DIR = Path(ung_nodes.__file__).resolve().parent / "ung_fixtures"


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True))


def load_cases():
    params = []
    for entry in ung_nodes.NODES:
        path = FIXTURES_DIR / f"{entry['id']}.json"
        cases = json.loads(path.read_text(encoding="utf-8"))
        for index, case in enumerate(cases):
            params.append(pytest.param(entry, case, id=f"{entry['id']}[{index}]"))
    return params


def test_every_node_has_a_fixture_with_two_cases():
    assert ung_nodes.NODES, "NODES must not be empty"
    for entry in ung_nodes.NODES:
        path = FIXTURES_DIR / f"{entry['id']}.json"
        assert path.is_file(), f"missing fixture {path}"
        cases = json.loads(path.read_text(encoding="utf-8"))
        assert len(cases) >= 2, f"{entry['id']} needs >= 2 fixture cases"


@pytest.mark.parametrize("entry,case", load_cases())
def test_fixture_case(entry, case):
    observed = entry["fn"](**case["inputs"], **case["parameters"])
    assert canonical(observed) == canonical(case["expect"])
