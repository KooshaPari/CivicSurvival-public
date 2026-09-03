#!/usr/bin/env python3
"""distill_intents.py — reproducible codex intent mining.

Walks every *.jsonl under the sessions root (defaults to
~/.codex/sessions/), extracts user-role response_item entries, filters
to prompts mentioning civic/CivicSurvival/gameplay/toolchain keywords,
and writes the result to a single markdown file.

Usage:
    python scripts/distill_intents.py \
        --sessions ~/.codex/sessions/ \
        --out docs/codex-intent-vs-shipped.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CIVIC_RE = re.compile(
    r"(civicsurvival|civic[\s_-]survival|0\.3\.\d+|"
    r"skyve|bepinex|paradox|cities[\s_-]?skylines|\bcs2\b|modding|"
    r"toolchain|toolkit|unity|domain|merge|wave|threat|"
    r"scorecard|discipline|adr|release|localization|"
    r"telemetry|help[\s_-]portal|save[\s_-]format|harmony|priority|phase|"
    r"tutorial|tooltip|intent|mining|installer|lifecycle|"
    r"update|remove|demo|play|build|publish|pipeline|"
    r"package|cli|bin|feature[\s_-]gate|feature[\s_-]flag|"
    r"csharp|dotnet|nuget|manifest|discipline|"
    r"axiom|crisis|migration)",
    re.IGNORECASE,
)
MIN_LEN, MAX_LEN = 60, 8000


def iter_prompts(sessions_root: Path):
    for jl in sorted(sessions_root.rglob("*.jsonl")):
        try:
            with open(jl, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or len(line) < 30:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("type") != "response_item":
                        continue
                    p = obj.get("payload", {})
                    if p.get("role") != "user":
                        continue
                    content = p.get("content", [])
                    text = ""
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict):
                                text = c.get("text", "") or c.get("input_text", "")
                                if text:
                                    break
                    elif isinstance(content, str):
                        text = content
                    text = text.strip()
                    if not text or len(text) < MIN_LEN or len(text) > MAX_LEN:
                        continue
                    if not CIVIC_RE.search(text):
                        continue
                    yield jl, text
        except OSError as e:
            print(f"  ERROR {jl.name}: {e}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--sessions",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Root directory containing codex session .jsonl files",
    )
    ap.add_argument(
        "--out",
        default="docs/codex-intent-vs-shipped.md",
        help="Markdown output path",
    )
    args = ap.parse_args()

    sessions = Path(args.sessions)
    if not sessions.exists():
        print(f"sessions root not found: {sessions}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Codex user prompts mentioning CivicSurvival-public\n\n")
        f.write(
            f"Mined from `~/.codex/sessions/` (filtered to `payload.role=user`, length {MIN_LEN}-{MAX_LEN}, civic-keyword match).\n\n---\n\n"
        )
        for jl, text in iter_prompts(sessions):
            f.write(f"## [{jl.name[:40]}] (line len {len(text)})\n\n{text}\n\n---\n\n")
            n += 1

    print(f"Wrote {n} prompts to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
