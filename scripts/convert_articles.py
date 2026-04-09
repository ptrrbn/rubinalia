#!/usr/bin/env python3
"""
Convert site_backup/writing/*.html to Jekyll _writing/ collection items.
Run from repo root: python3 scripts/convert_articles.py
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

WRITING_SRC = Path("site_backup/writing")
WRITING_DST = Path("_writing")
CATEGORY_FILES = ["features", "music", "film", "crit", "other"]

# Non-article files to skip
SKIP_FILES = {
    "index.html", "features.html", "music.html", "film.html",
    "crit.html", "other.html", "rubinresume.pdf",
    "feedbamboozledclip.html", "vliferwandaclip.html",
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


def parse_index_metadata():
    """
    Read each category index page and return:
    { "filename.html": {"publication": str, "date": "YYYY-MM-DD", "category": str} }
    Publication and date are parsed from <a href="file.html">...<i>Pub</i>, Month Year</a>.
    First category match wins (an article may appear in multiple indexes).
    """
    metadata = {}
    for category in CATEGORY_FILES:
        index_path = WRITING_SRC / f"{category}.html"
        if not index_path.exists():
            continue
        soup = BeautifulSoup(index_path.read_text(encoding="latin-1"), "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if not href.endswith(".html") or "/" in href:
                continue
            filename = href
            if filename in SKIP_FILES:
                continue
            italic = link.find("i")
            if not italic:
                continue
            publication = italic.get_text().strip()
            after = italic.next_sibling
            if not isinstance(after, NavigableString):
                continue
            date_text = str(after).strip().lstrip(",").strip()
            match = re.match(r"([A-Za-z]+)(?:/[A-Za-z]+)?\s+(\d{4})", date_text)
            if not match:
                continue
            month = MONTH_MAP.get(match.group(1), 1)
            year = int(match.group(2))
            if filename not in metadata:
                metadata[filename] = {
                    "publication": publication,
                    "date": f"{year}-{month:02d}-01",
                    "category": category,
                }
    return metadata


def extract_title(soup):
    """Return plain text title from <div class="hed">, collapsing inline HTML."""
    hed = soup.find("div", class_="hed")
    if not hed:
        return ""
    return re.sub(r"\s+", " ", hed.get_text(separator=" ")).strip()


def extract_dek(soup):
    """Return dek text from <div class="dek">, stripping trailing 'by Peter Rubin' line."""
    dek_div = soup.find("div", class_="dek")
    if not dek_div:
        return ""
    text = dek_div.get_text(separator="\n").strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines and lines[-1].lower().startswith("by "):
        lines = lines[:-1]
    return " ".join(lines).strip()


def extract_body(soup):
    """
    Return inner HTML of the article body:
    - Includes <div id="photo"> (lead image) if present
    - Includes <div id="content"> with hed/dek removed (they go in front matter)
    - Rewrites ../images/ -> /assets/images/
    """
    parts = []
    photo = soup.find("div", id="photo")
    if photo:
        parts.append(str(photo))
    content = soup.find("div", id="content")
    if not content:
        return ""
    for tag in content.find_all("div", class_=["hed", "dek"]):
        tag.decompose()
    parts.append(content.decode_contents())
    body = "\n".join(parts)
    body = body.replace("../images/", "/assets/images/")
    body = re.sub(r'src="https?://(?:www\.)?rubinalia\.com/images/', 'src="/assets/images/', body)
    return body.strip()


def convert_article(src_path, meta):
    """
    Read src_path HTML, return Jekyll-ready string:
    YAML front matter + stripped article body.
    meta: {"publication": str, "date": "YYYY-MM-DD", "category": str}
    """
    soup = BeautifulSoup(src_path.read_text(encoding="latin-1"), "html.parser")
    title = extract_title(soup).replace('"', '\\"')
    dek = extract_dek(soup).replace('"', '\\"')
    body = extract_body(soup)
    front_matter = (
        f'---\n'
        f'title: "{title}"\n'
        f'dek: "{dek}"\n'
        f'publication: {meta["publication"]}\n'
        f'date: {meta["date"]}\n'
        f'category: {meta["category"]}\n'
        f'---'
    )
    return f"{front_matter}\n\n{body}"


def main():
    WRITING_DST.mkdir(exist_ok=True)
    metadata = parse_index_metadata()
    unmatched = []
    converted = 0

    for src in sorted(WRITING_SRC.glob("*.html")):
        if src.name in SKIP_FILES:
            continue
        meta = metadata.get(src.name)
        if not meta:
            unmatched.append(src.name)
            meta = {"publication": "UNKNOWN", "date": "1900-01-01", "category": "other"}
        dst = WRITING_DST / src.name
        dst.write_text(convert_article(src, meta), encoding="utf-8")
        print(f"  ✓ {src.name}")
        converted += 1

    print(f"\nConverted {converted} articles.")
    if unmatched:
        print(f"\n⚠ {len(unmatched)} articles not in any category index (marked 'other', date 1900-01-01):")
        for f in unmatched:
            print(f"  - _writing/{Path(f).stem}.html")
        print("  → Open these files and manually set publication, date, and category.")


if __name__ == "__main__":
    main()
