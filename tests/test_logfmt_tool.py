"""Offline tests for logfmt parsing, serialization, filtering, and stats."""

from __future__ import annotations

from pathlib import Path

from logfmt_tool import (compute_stats, filter_records, parse, parse_line,
                         select, to_logfmt)

EX = Path(__file__).resolve().parent.parent / "examples" / "app.log"


def test_parse_simple():
    assert parse_line("level=info port=8080") == {"level": "info", "port": "8080"}


def test_parse_quoted_value_with_spaces():
    assert parse_line('msg="user logged in" id=42') == {"msg": "user logged in", "id": "42"}


def test_parse_escapes():
    # backslash escapes are processed INSIDE quotes ...
    assert parse_line(r'msg="he said \"hi\""') == {"msg": 'he said "hi"'}
    assert parse_line(r'p="c:\\tmp"') == {"p": r"c:\tmp"}
    # ... but unquoted values are taken literally (no escape processing)
    assert parse_line(r'path=c:\temp') == {"path": r"c:\temp"}


def test_parse_bare_key_and_empty_value():
    assert parse_line("ok level=") == {"ok": True, "level": ""}


def test_parse_duplicate_last_wins():
    assert parse_line("a=1 a=2") == {"a": "2"}


def test_parse_equals_inside_quotes():
    assert parse_line('q="a=b&c=d" n=1') == {"q": "a=b&c=d", "n": "1"}


def test_to_logfmt_roundtrip():
    rec = {"level": "info", "msg": "hello world", "n": "5", "empty": ""}
    line = to_logfmt(rec)
    assert line == 'level=info msg="hello world" n=5 empty=""'
    assert parse_line(line) == rec


def test_to_logfmt_bools():
    assert to_logfmt({"ok": True, "bad": False}) == "ok=true bad=false"


def test_filter_equality_and_exists():
    recs = parse(EX.read_text(encoding="utf-8"))
    errors = filter_records(recs, "level=error")
    assert len(errors) == 2 and all(r["level"] == "error" for r in errors)
    has_retry = filter_records(recs, "retry")
    assert len(has_retry) == 1


def test_filter_numeric():
    recs = parse(EX.read_text(encoding="utf-8"))
    slow = filter_records(recs, "elapsed_ms>=100")
    assert len(slow) == 1 and slow[0]["path"] == "/users"
    server_err = filter_records(recs, "status>=500")
    assert len(server_err) == 2


def test_filter_not_equal():
    recs = parse(EX.read_text(encoding="utf-8"))
    non_info = filter_records(recs, "level!=info")
    assert all(r["level"] != "info" for r in non_info)
    assert len(non_info) == 3


def test_select_projection():
    rec = {"level": "info", "msg": "x", "status": "200"}
    assert select(rec, ["level", "status", "missing"]) == {"level": "info", "status": "200"}


def test_stats():
    recs = parse(EX.read_text(encoding="utf-8"))
    s = compute_stats(recs)
    assert s["records"] == 6
    assert s["keys"]["level"]["present"] == 6
    assert s["keys"]["level"]["distinct"] == 3
    # 'status' present in 5 of 6 lines
    assert s["keys"]["status"]["present"] == 5
    top_levels = dict(s["keys"]["level"]["top"])
    assert top_levels["info"] == 3 and top_levels["error"] == 2
