## What does this PR do?

<!-- Parser edge case? new filter operator? output format? -->

## Checklist

- [ ] Tests added/updated and `pytest -q` passes (offline)
- [ ] `python -m compileall logfmt_tool` is clean
- [ ] Real logfmt semantics preserved (quoted escapes, bare flags, last-wins)
- [ ] Stays dependency-free (re + collections + argparse)
