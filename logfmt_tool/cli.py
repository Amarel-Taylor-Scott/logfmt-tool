"""logfmt-tool CLI — parse / filter / select / stats over logfmt logs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .__version__ import __version__
from .core import (compute_stats, filter_records, parse, select, to_logfmt)


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def _emit(records, as_json: bool, jsonl: bool) -> None:
    if jsonl:
        for r in records:
            print(json.dumps(r))
    elif as_json:
        print(json.dumps(records, indent=2))
    else:
        for r in records:
            print(to_logfmt(r))


def cmd_parse(args: argparse.Namespace) -> int:
    records = parse(_read(args.input))
    _emit(records, as_json=not args.jsonl, jsonl=args.jsonl)
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    records = filter_records(parse(_read(args.input)), args.expr)
    _emit(records, as_json=args.json, jsonl=args.jsonl)
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    records = [select(r, keys) for r in parse(_read(args.input))]
    _emit(records, as_json=args.json, jsonl=args.jsonl)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    print(json.dumps(compute_stats(parse(_read(args.input)), top=args.top), indent=2))
    return 0


def cmd_version(_: argparse.Namespace) -> int:
    print(f"logfmt-tool {__version__}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logfmt",
        description="Parse, filter, select, and summarize logfmt (key=value) logs.",
    )
    p.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")

    pp = sub.add_parser("parse", help="Parse logfmt -> JSON")
    pp.add_argument("input", nargs="?", default="-", help="logfmt file or '-' for stdin")
    pp.add_argument("--jsonl", action="store_true", help="One JSON object per line")
    pp.set_defaults(func=cmd_parse)

    pf = sub.add_parser("filter", help="Keep records matching EXPR (e.g. level=error, status>=500)")
    pf.add_argument("expr")
    pf.add_argument("input", nargs="?", default="-")
    pf.add_argument("--json", action="store_true", help="Emit JSON array instead of logfmt")
    pf.add_argument("--jsonl", action="store_true", help="Emit JSONL instead of logfmt")
    pf.set_defaults(func=cmd_filter)

    ps = sub.add_parser("select", help="Project only KEYS (comma-separated)")
    ps.add_argument("keys")
    ps.add_argument("input", nargs="?", default="-")
    ps.add_argument("--json", action="store_true")
    ps.add_argument("--jsonl", action="store_true")
    ps.set_defaults(func=cmd_select)

    pt = sub.add_parser("stats", help="Per-key presence / distinct / top values")
    pt.add_argument("input", nargs="?", default="-")
    pt.add_argument("--top", type=int, default=5, help="Top N values per key")
    pt.set_defaults(func=cmd_stats)

    sub.add_parser("version", help="Print version").set_defaults(func=cmd_version)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
