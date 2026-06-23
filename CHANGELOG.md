# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-23

### Added
- `parse_line` / `parse` — full logfmt parsing (quoted values with `\"`/`\\` escapes,
  empty values, bare present-flags, duplicate-key last-wins).
- `to_logfmt` — serialize a record back to logfmt, quoting only values that need it.
- `filter_records` (`=`, `!=`, `>`, `<`, `>=`, `<=`, and bare key-exists), `select`, and
  `compute_stats` (per-key presence / distinct / top values).
- CLI `logfmt`: `parse`, `filter`, `select`, `stats` — output as logfmt, JSON, or JSONL.
- Pure-standard-library implementation (re + collections + argparse), offline test suite,
  and CI on Python 3.10–3.12.

[0.1.0]: https://github.com/Amarel-Taylor-Scott/logfmt-tool/releases/tag/v0.1.0
