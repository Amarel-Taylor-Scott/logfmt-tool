"""logfmt-tool — parse, query, and emit logfmt key=value logs (pure stdlib)."""

from __future__ import annotations

from .__version__ import __version__
from .core import (compute_stats, filter_records, match, parse, parse_filter,
                   parse_line, select, to_logfmt)

__all__ = [
    "__version__", "parse", "parse_line", "to_logfmt",
    "filter_records", "parse_filter", "match", "select", "compute_stats",
]
