"""NotImplementedException + unfinished-code discipline suite.

Locks in the contract that hand-written source code contains no:
  * NotImplementedException throws (catches incomplete implementations)
  * TODO / FIXME / XXX / HACK markers (catches unfinished work)
  * Console.WriteLine debug statements (catches forgotten debug code)
  * `// DEBUG: ...` markers (catches forgotten debug scaffolding)
  * Empty method bodies (`public void X() {}` with no statements)

The auto-generated Unity ECS source under CivicSurvival/obj/Generated/ is excluded —
it's machine-written boilerplate that gets regenerated on every build.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("CivicSurvival")


def _is_generated(p: Path) -> bool:
    """True if the file is auto-generated (Unity ECS source generator, etc.)."""
    return "obj" in p.parts or "bin" in p.parts


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def _all_source_files() -> list[Path]:
    return [p for p in ROOT.rglob("*.cs") if not _is_generated(p)]


def test_no_not_implemented_exception_in_source() -> None:
    """Zero `throw new NotImplementedException` or `NotImplementedException()` in source.

    Auto-generated files under obj/Generated/ are excluded — they ship from the
    Unity ECS source generator with NotImplementedException stubs in entity wrappers,
    and those are intentional placeholders (the runtime path is generated to call our
    user's OnUpdate via the ISystem interface).

    A regression that adds `throw new NotImplementedException()` to hand-written code
    is a clear "I forgot to finish this" signal and must be caught at PR time.
    """
    offenders = []
    pattern = re.compile(r"\bNotImplementedException\b")
    for cs in _all_source_files():
        if pattern.search(_read(cs)):
            offenders.append(str(cs))
    assert not offenders, (
        f"Files containing `NotImplementedException`: {offenders}. "
        f"Either implement the missing code, mark the method as `abstract`, or use "
        f'`throw new InvalidOperationException("not yet implemented")` if the gap is '
        f"intentional. Never `throw new NotImplementedException()` in shipped code."
    )


def test_no_todo_fixme_xxx_hack_markers() -> None:
    """Zero TODO/FIXME/XXX/HACK markers in source files.

    These markers accumulate silently and signal unfinished work. A discipline test
    forces every contributor to either:
      - Resolve the marker (delete it when work is complete)
      - Convert it to a tracked issue (file an issue, link it in the marker text)

    Note: a doc comment MAY mention `TODO` as part of an explanatory note (e.g. the
    "how to add a domain" guide mentions TODOs). The test catches the marker at the
    start of a comment line or as a standalone word, not in flowing prose.
    """
    pattern = re.compile(r"^\s*(//|\*)\s*(TODO|FIXME|XXX|HACK)\b", re.MULTILINE | re.IGNORECASE)
    offenders = []
    for cs in _all_source_files():
        matches = pattern.findall(_read(cs))
        if matches:
            # Find the line numbers too.
            text = _read(cs)
            line_nums = []
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.match(line):
                    line_nums.append(i)
            offenders.append((str(cs), line_nums))
    assert not offenders, (
        f"Files containing TODO/FIXME/XXX/HACK markers: {offenders}. "
        f"Resolve the work, file an issue, or use a `// NOTE:` annotation instead."
    )


def test_no_console_writeline_in_source() -> None:
    """Zero `Console.WriteLine` in source.

    CivicSurvival uses Colossal.Logging (Log.Info/Log.Warn/Log.Error), not Console.WriteLine.
    A `Console.WriteLine` left in is a sign of either (a) debugging scaffolding the
    contributor forgot to remove, or (b) a need that wasn't met by the mod's logger.

    Tests catch both cases: PR-time feedback says "use Log.Info(...) or delete this".
    """
    pattern = re.compile(r"\bConsole\.WriteLine\b")
    offenders = []
    for cs in _all_source_files():
        if pattern.search(_read(cs)):
            offenders.append(str(cs))
    assert not offenders, (
        f"Files containing `Console.WriteLine`: {offenders}. "
        f"Use `Log.Info(...)` / `Log.Warn(...)` / `Log.Error(...)` from the "
        f"Colossal.Logging API (see `Mod.Log` for the mod-level logger)."
    )


def test_no_debug_only_prints() -> None:
    """Zero `System.Diagnostics.Debug.Print` or `Debug.WriteLine` calls in source.

    Same rationale as Console.WriteLine — use the mod's logger so output goes to
    CivicSurvival.log (and Sentry on Error+), not to the player's debugger.
    """
    pattern = re.compile(r"\b(System\.Diagnostics\.Debug|^\s*Debug)\.(Print|WriteLine|Write)\b")
    offenders = []
    for cs in _all_source_files():
        if pattern.search(_read(cs)):
            offenders.append(str(cs))
    assert not offenders, (
        f"Files containing `Debug.Print/WriteLine/Write`: {offenders}. "
        f"Use Log.Info/Log.Warn/Log.Error instead so output flows through CivicSurvival.log."
    )


def test_no_public_void_method_with_empty_body() -> None:
    """No undocumented `public void Foo() { }` (empty body, no statements).

    Empty public methods are a smell — they often mean "I'll come back to this"
    and ship as silent no-ops. EXCEPTION: the method has a `///` doc comment
    immediately above it explaining the no-op (e.g. an explicit interface
    implementation that doesn't need a particular hook).

    Without this guard, the discipline test forces the contributor to either
    implement the method or mark it private/internal with a justification.
    """
    pattern = re.compile(
        r"\bpublic\s+(?:override\s+|virtual\s+|async\s+|static\s+)*void\s+(\w+)\s*\([^)]*\)\s*\{\s*\}"
    )
    offenders = []
    for cs in _all_source_files():
        text = _read(cs)
        for m in pattern.finditer(text):
            start = m.start()
            line_num = text[:start].count("\n") + 1
            # Look at the lines BEFORE the method to see if there's a `///` doc block
            # immediately preceding it (with at most blank lines between).
            lines_before = text[:start].splitlines()
            has_doc = False
            for prev_line in reversed(lines_before):
                stripped = prev_line.strip()
                if not stripped:
                    continue
                if stripped.startswith("///"):
                    has_doc = True
                break
            if has_doc:
                continue
            offenders.append((str(cs), line_num, m.group(1)))
    assert not offenders, (
        f"Empty `public void` methods without documentation: {offenders}. "
        f"Either implement the method, or add a `/// <summary>` doc comment immediately "
        f"above it explaining why it's a deliberate no-op."
    )


def test_no_throw_new_exception_with_no_message() -> None:
    """No `throw new SomeException()` (no message argument).

    A bare `throw new InvalidOperationException()` tells the player nothing about
    what went wrong. CivicSurvival's contract (per CLAUDE.md and the telemetry
    documentation) is that every thrown exception includes a diagnostic message.

    Tests catch the pattern at compile time rather than waiting for a player report.
    """
    pattern = re.compile(
        r"\bthrow\s+new\s+(?:Exception|InvalidOperationException|NotSupportedException|ArgumentException|InvalidCastException)\s*\(\s*\)\s*;"
    )
    offenders = []
    for cs in _all_source_files():
        text = _read(cs)
        for m in pattern.finditer(text):
            line_num = text[: m.start()].count("\n") + 1
            offenders.append((str(cs), line_num, m.group(0).strip()))
    assert not offenders, (
        f"Bare `throw new X()` without a diagnostic message: {offenders}. "
        f"Every exception must include a message explaining what went wrong."
    )


if __name__ == "__main__":
    import subprocess
    import sys

    rc = subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"])
    sys.exit(rc)
