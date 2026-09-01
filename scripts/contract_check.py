#!/usr/bin/env python3
"""Public-snapshot contract integrity checks; no licensed host is required."""

from pathlib import Path
import os
import re
import sys


ROOT = Path(os.environ.get("CIVIC_REPO_ROOT", Path(__file__).resolve().parents[1]))
SOURCES = [
    ROOT / "CivicSurvival/Core/UI/BindingNames.cs",
    ROOT / "CivicSurvival/Core/UI/BindingNames.Dto.g.cs",
    ROOT / "CivicSurvival/Core/UI/BindingNames.Trigger.g.cs",
]
GENERATED = ROOT / "CivicSurvival/UI/src/hooks/bindingNames.generated.ts"


def main() -> int:
    required = [
        ROOT / "CivicSurvival.sln",
        ROOT / "CivicSurvival.Contracts/CivicSurvival.Contracts.csproj",
        *SOURCES,
        GENERATED,
        ROOT / "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
        ROOT / "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        print("missing public contract artifacts: " + ", ".join(missing), file=sys.stderr)
        return 1
    source_entries = [
        match
        for source in SOURCES
        for match in re.findall(
            r'public\s+const\s+string\s+(\w+)\s*=\s*"([^"]+)"', source.read_text()
        )
    ]
    source_map = dict(source_entries)
    generated_text = GENERATED.read_text()
    object_match = re.search(r"export const B = \{([\s\S]*?)\n\} as const;", generated_text)
    if not object_match:
        print("generated binding object is missing", file=sys.stderr)
        return 1
    generated_map = dict(
        re.findall(r'^\s+(\w+)\s*:\s*"([^"]+)"\s*,?$', object_match.group(1), re.MULTILINE)
    )
    missing_values = sorted(set(source_map) - set(generated_map))
    unexpected_values = sorted(set(generated_map) - set(source_map))
    mismatched_values = sorted(
        key for key in source_map if key in generated_map and source_map[key] != generated_map[key]
    )
    if (
        missing_values
        or unexpected_values
        or mismatched_values
        or len(generated_map) != len(source_map)
    ):
        print(
            "binding projection mismatch; missing: "
            + ", ".join(missing_values or ["none"])
            + "; unexpected: "
            + ", ".join(unexpected_values or ["none"])
            + "; mismatched: "
            + ", ".join(mismatched_values or ["none"]),
            file=sys.stderr,
        )
        return 1
    projection_paths = [
        ROOT / "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
        ROOT / "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
    ]
    if any(not path.is_file() or not path.read_text().strip() for path in projection_paths):
        print("generated contract projection is missing or empty", file=sys.stderr)
        return 1
    print(
        f"contract check passed: {len(source_map)} C# binding values represented in generated TypeScript"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
