"""Replace -- with em dashes in article body content only (not frontmatter)."""

import re
from pathlib import Path

WRITING_DIR = Path(__file__).parent.parent / "_writing"

# Match exactly two hyphens, not part of a longer run (e.g. ---)
DOUBLE_HYPHEN = re.compile(r"(?<!-)--(?!-)")


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")

    # Split off frontmatter (content between the opening --- and closing ---)
    # Files start with "---\n" and have a second "---\n" ending the frontmatter.
    if not text.startswith("---"):
        print(f"  SKIP (no frontmatter): {path.name}")
        return False

    # Find the end of frontmatter
    end = text.index("---", 3)  # skip the opening ---
    frontmatter = text[: end + 3]
    body = text[end + 3 :]

    new_body = DOUBLE_HYPHEN.sub("\u2014", body)

    if new_body == body:
        return False

    path.write_text(frontmatter + new_body, encoding="utf-8")
    count = len(DOUBLE_HYPHEN.findall(body))
    print(f"  {path.name}: {count} replacement(s)")
    return True


if __name__ == "__main__":
    changed = 0
    for f in sorted(WRITING_DIR.glob("*.html")):
        if fix_file(f):
            changed += 1
    print(f"\nDone. {changed} file(s) updated.")
