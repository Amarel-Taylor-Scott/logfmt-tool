# Contributing

Thanks for helping improve **logfmt-tool**!

## Dev setup

```bash
pip install -e ".[dev]"
pytest -q                    # fully offline
```

## Where things live

- **Parser, serializer, filter, select, stats** -> `logfmt_tool/core.py`
- **CLI (`parse`/`filter`/`select`/`stats`/`version`)** -> `logfmt_tool/cli.py`

Keep it **dependency-free** (re + collections + argparse).

## Design rules

- Match real **logfmt** semantics: escapes only apply inside quotes; unquoted values are
  literal; bare keys are present-flags; duplicate keys are last-wins.
- New parsing behavior comes with a `parse_line` test covering the exact bytes; new filter
  operators come with equality **and** boundary tests.

## Reporting issues

Use the issue templates. For anything security-sensitive, see [SECURITY.md](SECURITY.md).
