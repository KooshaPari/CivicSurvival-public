import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
TASKS = ROOT / ".agileplus/civic-warfare-program/tasks"


def test_late_work_package_titles_match_frontmatter_and_headings():
    for wp_id in ("WP10", "WP14", "WP15", "WP16", "WP17", "WP18", "WP19", "WP20"):
        path = next(TASKS.glob(f"{wp_id}-*.md"))
        text = path.read_text()
        frontmatter = re.search(r"^title: (.+) \(%s\)$" % wp_id, text, re.MULTILINE)
        heading = re.search(r"^# Work Package: (.+) \(%s\)$" % wp_id, text, re.MULTILINE)
        assert frontmatter and heading, path
        assert frontmatter.group(1) == heading.group(1)
        assert len(frontmatter.group(1)) > 40
