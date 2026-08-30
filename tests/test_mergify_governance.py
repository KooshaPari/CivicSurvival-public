from pathlib import Path


ROOT = Path(__file__).parents[1]
MERGIFY = ROOT / ".mergify.yml"
REQUIRED_CHECKS = {
    'check-success = "Civic Evidence Gate"',
    'check-success = "Security Scan"',
    'check-success = "Dependency Delta"',
    'check-success = "ci / lint"',
    'check-success = "ci / test"',
    'check-success = "CodeRabbit"',
    'check-success = "Kilo Code Review"',
}


def _rule_conditions(config: str, rule_name: str) -> set[str]:
    rule = config.split(f"  - name: {rule_name}\n", 1)[1]
    conditions = rule.split("    conditions:\n", 1)[1].split("    actions:\n", 1)[0]
    return {
        line.removeprefix("      - ")
        for line in conditions.splitlines()
        if line.startswith("      - ")
    }


def test_merge_and_ready_rules_require_current_head_bot_gates():
    config = MERGIFY.read_text()

    for rule_name in (
        "Auto-merge when protected checks are green",
        "Add ready-to-merge label",
    ):
        conditions = _rule_conditions(config, rule_name)
        assert REQUIRED_CHECKS <= conditions
        assert {"base=main", "-draft", "-conflict", "-closed"} <= conditions
