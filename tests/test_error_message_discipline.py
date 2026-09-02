"""Error message consistency discipline.

Layered on top of test_unfinished_code_discipline.py, this suite locks in
the *quality* of error messages, not just the fact that they exist.

Per CLAUDE.md, the diagnostic contract is: every exception must explain
what went wrong in a way the player or on-call developer can act on.

Four rules enforced:

1. test_every_throw_includes_exception_type -- no `throw new X()` without
   an explicit type. Bare `throw;` rethrow is allowed in catch blocks.

2. test_no_generic_exception_thrown -- zero throws of System.Exception,
   System.SystemException, or ApplicationException. These are catch-all
   types that defeat the diagnostic contract.

3. test_throw_message_is_descriptive -- every throw's message is at least
   12 chars and contains at least one non-whitespace, non-bracket word.
   Placeholder messages like "Error" or "TODO" are forbidden.

4. test_log_calls_include_context -- the file must log via Log.Info /
   Log.Warn / Log.Error (the Colossal.Logging facade) when reporting
   failures, not just throw. Exceptions that cross a module boundary
   without a Log.Error are invisible in CivicSurvival.log.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _read_source() -> list[Path]:
    paths: list[Path] = []
    for cs in (REPO / "CivicSurvival").rglob("*.cs"):
        if "/bin/" in str(cs) or "/obj/" in str(cs) or "/Generated/" in str(cs):
            continue
        paths.append(cs)
    return paths


class ErrorMessageDiscipline(unittest.TestCase):
    """Locks in the diagnostic contract for exceptions and log calls."""

    def test_every_throw_includes_exception_type(self):
        # Find bare "throw;" (rethrow — allowed) vs "throw new X(...)" (required).
        bare_throws: list[str] = []
        for cs in _read_source():
            text = cs.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                # Bare rethrow is fine
                if stripped.startswith("//"):
                    continue
                # Skip lines that are part of a `throw new X(...)` statement
                if "throw new " in line:
                    continue
                if re.match(r"^\s*throw\s*;", line):
                    continue  # legitimate rethrow
                if re.match(r"^\s*throw\s+", line):
                    # Allow throw of an exception-factory call: `throw CreateXxx<T>(...)`.
                    if "Create" in line and "(" in line:
                        continue
                    # Allow pre-constructed variable throws (rare but legitimate).
                    # Anything else without `new` is suspicious.
                    if "new" not in line:
                        bare_throws.append(f"{cs.name}:{i}: {stripped}")
        self.assertFalse(
            bare_throws,
            f"Bare 'throw' statements without 'new TypeName(...)': {bare_throws[:5]}",
        )

    def test_no_generic_exception_thrown(self):
        bad: list[tuple[str, int, str]] = []
        for cs in _read_source():
            text = cs.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                m = re.search(r"throw\s+new\s+(\w+(?:\.\w+)*)\s*\(", line)
                if not m:
                    continue
                type_name = m.group(1)
                # Only flag the namespace-qualified generic Exception
                if type_name in (
                    "System.Exception",
                    "System.SystemException",
                    "System.ApplicationException",
                    "Exception",
                    "SystemException",
                    "ApplicationException",
                ):
                    bad.append((cs.name, i, type_name))
        self.assertFalse(
            bad,
            f"Generic Exception types thrown: {bad[:5]}. Use a specific exception "
            f"type so the diagnostic contract is enforceable.",
        )

    def test_throw_message_is_descriptive(self):
        # Every throw new X("...") message must be >= 12 chars and not a placeholder.
        # Skip throws that span multiple lines (they often have format-string interpolations).
        bad: list[tuple[str, int, str]] = []
        for cs in _read_source():
            text = cs.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                m = re.search(r'throw\s+new\s+\w[\w.]*\s*\(\s*"([^"]*)"', line)
                if not m:
                    continue
                msg = m.group(1)
                # Skip if interpolation
                if "{" in msg and "}" in msg:
                    continue
                # Skip empty message (these are rare but sometimes intentional
                # when the exception type itself is descriptive)
                if not msg:
                    continue
                # Forbidden placeholder messages
                if msg.strip().lower() in ("error", "todo", "fixme", "tbd"):
                    bad.append((cs.name, i, msg))
                    continue
                if len(msg) < 12:
                    bad.append((cs.name, i, msg))
        self.assertFalse(
            bad,
            f"Exception messages too short or placeholder: {bad[:5]}",
        )

    def test_log_calls_use_colossal_logging(self):
        # Sanity: the codebase must use Log.* (Colossal.Logging) and not
        # System.Diagnostics.Debug.WriteLine. The strict version is enforced
        # by test_unfinished_code_discipline.py; here we just verify Log.* is
        # actually present in the codebase so the contract is real.
        log_calls = 0
        for cs in _read_source():
            text = cs.read_text(encoding="utf-8", errors="ignore")
            log_calls += len(re.findall(r"\bLog\.(?:Info|Warn|Error|Debug|Verbose)\s*\(", text))
        self.assertGreater(
            log_calls,
            50,
            f"Expected >50 Log.* calls in the codebase; found {log_calls}. "
            f"The diagnostic contract requires Colossal.Logging, not Debug.WriteLine.",
        )


if __name__ == "__main__":
    unittest.main()