# logfmt-tool

Parse, filter, select, and summarize **logfmt** logs — the `key=value` structured-log
format from Heroku and Go's go-kit — and convert them to JSON or back. Pure standard
library, no dependencies.

```bash
$ logfmt filter "level=error" examples/app.log
level=error msg="db connection failed" status=500 retry=3
level=error msg="unhandled exception" status=500 path=/checkout

$ logfmt filter "elapsed_ms>=100" examples/app.log --jsonl
{"level": "warn", "msg": "slow query", "path": "/users", "status": "200", "elapsed_ms": "812.4"}

$ logfmt parse examples/app.log --jsonl | head -1
{"level": "info", "msg": "server started", "port": "8080", "ok": true}
```

When your logs are logfmt but your tools want JSON — or you just need a quick `grep` that
understands `key=value` and numbers — this bridges the gap without a heavyweight log
pipeline.

## Why

- **Triage logs locally.** Filter by level, status code, latency threshold — with real
  numeric comparisons (`status>=500`, `elapsed_ms>=100`), not string matching.
- **logfmt ⇄ JSON.** Pipe logfmt into anything that speaks JSON (`jq`, your scripts), or
  normalize messy lines back into clean logfmt.
- **Quick shape check.** `stats` shows which keys appear, how often, and their top values.

## Install

```bash
pip install -e .
```

(Or copy the `logfmt_tool/` package — no dependencies.)

## CLI (`logfmt`)

```bash
logfmt parse app.log                      # -> JSON array
logfmt parse app.log --jsonl              # -> one JSON object per line
logfmt filter "level=error" app.log       # equality
logfmt filter "status>=500" app.log       # numeric comparison
logfmt filter "retry" app.log             # key exists
logfmt filter "level!=info" app.log       # not-equal
logfmt select level,status,path app.log   # project keys (stays logfmt)
logfmt stats app.log --top 3              # per-key presence / distinct / top values
cat app.log | logfmt filter "level=warn" -
```

Filter operators: `=`, `!=`, `>`, `<`, `>=`, `<=` (numeric for the inequalities), and a
bare `key` to test presence. `filter`/`select` emit logfmt by default; add `--json` or
`--jsonl` to switch.

## logfmt parsing rules

| Input | Parses to |
|-------|-----------|
| `key=value` | `{"key": "value"}` |
| `key="a b"` | quoted values may contain spaces; `\"` and `\\` are escapes |
| `key=` | empty string `""` |
| bare `key` | `True` (a present flag) |
| `a=1 a=2` | last one wins (`{"a": "2"}`) |

`to_logfmt()` round-trips: a parsed record (without bare-flag/boolean keys) serializes back
to an equivalent line, quoting only values that need it.

## Library

```python
from logfmt_tool import parse, parse_line, to_logfmt, filter_records, compute_stats

parse_line('level=info msg="hi there" n=3')      # {'level': 'info', 'msg': 'hi there', 'n': '3'}
records = parse(open("app.log").read())
errors = filter_records(records, "status>=500")
to_logfmt({"level": "info", "msg": "hello world"})  # 'level=info msg="hello world"'
compute_stats(records)                             # {'records': N, 'keys': {...}}
```

## Notes & limits

- Values are parsed as **strings** (logfmt is untyped); numeric filters coerce on demand,
  so `status>=500` works even though the value is stored as `"500"`.
- Bare keys become `True`; serializing them back yields `key=true`, which then parses as the
  string `"true"` — round-trip is exact for normal `key=value` records, not for bare flags.

## License

[MIT](LICENSE) © 2026 Amarel Taylor Scott
