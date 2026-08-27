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
    source_values = set().union(*(set(re.findall(r'public\s+const\s+string\s+\w+\s*=\s*"([^"]+)"', source.read_text())) for source in SOURCES))
    generated_text = GENERATED.read_text()
    object_match = re.search(r"export const B = \{([\s\S]*?)\n\} as const;", generated_text)
    if not object_match:
        print("generated binding object is missing", file=sys.stderr)
        return 1
    generated_values = set(re.findall(r'^\s+\w+\s*:\s*"([^"]+)"\s*,?$', object_match.group(1), re.MULTILINE))
    missing_values = sorted(source_values - generated_values)
    unexpected_values = sorted(generated_values - source_values)
    if missing_values or unexpected_values or len(generated_values) != len(source_values):
        print("binding projection mismatch; missing: " + ", ".join(missing_values or ["none"]) + "; unexpected: " + ", ".join(unexpected_values or ["none"]), file=sys.stderr)
        return 1
    projection_paths = [
        ROOT / "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
        ROOT / "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
    ]
    if any(not path.is_file() or not path.read_text().strip() for path in projection_paths):
        print("generated contract projection is missing or empty", file=sys.stderr)
        return 1
    print(f"contract check passed: {len(source_values)} C# binding values represented in generated TypeScript")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
