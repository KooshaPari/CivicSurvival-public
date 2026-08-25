import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCORECARD = REPO_ROOT / "scripts" / "scorecard_ci.py"


def make_minimal_repo(root: Path) -> None:
    (root / "README.md").write_text("# fixture\n", encoding="utf-8")
    (root / "LICENSE").write_text("fixture\n", encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text("fixture\n", encoding="utf-8")
    (root / ".editorconfig").write_text("root = true\n", encoding="utf-8")
    (root / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "ci.yml").write_text("name: fixture\n", encoding="utf-8")


class ScorecardBaselineTests(unittest.TestCase):
    def test_fail_on_drop_uses_recorded_baseline_not_target_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            make_minimal_repo(fixture)
            baseline = fixture / "baseline.json"
            baseline.write_text(json.dumps({"score": 6, "total": 88}), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCORECARD),
                    str(fixture),
                    "--output",
                    "json",
                    "--threshold",
                    "85",
                    "--baseline-file",
                    str(baseline),
                    "--fail-on-drop",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["baseline_score"], 6)
            self.assertEqual(report["score_delta"], 0)
            self.assertFalse(report["regression"])

    def test_fail_on_drop_rejects_a_score_below_recorded_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            make_minimal_repo(fixture)
            baseline = fixture / "baseline.json"
            baseline.write_text(json.dumps({"score": 7, "total": 88}), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCORECARD),
                    str(fixture),
                    "--output",
                    "json",
                    "--baseline-file",
                    str(baseline),
                    "--fail-on-drop",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["regression"])
            self.assertEqual(report["score_delta"], -1)


if __name__ == "__main__":
    unittest.main()
