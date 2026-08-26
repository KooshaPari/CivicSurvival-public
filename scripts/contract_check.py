#!/usr/bin/env python3
"""Public-snapshot contract integrity checks; no licensed host is required."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CivicSurvival/Core/UI/BindingNames.cs"
GENERATED = ROOT / "CivicSurvival/UI/src/hooks/bindingNames.generated.ts"


def main() -> int:
    required = [
        ROOT / "CivicSurvival.sln",
        ROOT / "CivicSurvival.Contracts/CivicSurvival.Contracts.csproj",
        SOURCE,
        GENERATED,
        ROOT / "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
        ROOT / "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        print("missing public contract artifacts: " + ", ".join(missing), file=sys.stderr)
        return 1
    source_values = set(re.findall(r'public\s+const\s+string\s+\w+\s*=\s*"([^"]+)"', SOURCE.read_text()))
    generated_values = set(re.findall(r'\b\w+:\s*"([^"]+)"', GENERATED.read_text()))
    missing_values = sorted(source_values - generated_values)
    if missing_values:
        print("binding source values absent from generated TypeScript: " + ", ".join(missing_values), file=sys.stderr)
        return 1
    print(f"contract check passed: {len(source_values)} C# binding values represented in generated TypeScript")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
