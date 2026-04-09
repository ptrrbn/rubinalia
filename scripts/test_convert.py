#!/usr/bin/env python3
"""Tests for convert_articles.py. Run from repo root: python3 scripts/test_convert.py"""

import sys
sys.path.insert(0, "scripts")

from pathlib import Path
from bs4 import BeautifulSoup
from convert_articles import (
    parse_index_metadata,
    extract_title,
    extract_dek,
    extract_body,
    convert_article,
)


def test_parse_index_metadata_finds_known_articles():
    metadata = parse_index_metadata()
    assert "gqgarner.html" in metadata, "Jennifer Garner article should be in features index"
    g = metadata["gqgarner.html"]
    assert g["publication"] == "GQ", f"Expected GQ, got {g['publication']}"
    assert g["category"] == "features", f"Expected features, got {g['category']}"
    assert g["date"].startswith("200"), f"Expected 2000s date, got {g['date']}"
    print("PASS test_parse_index_metadata_finds_known_articles")


def test_parse_index_metadata_covers_multiple_categories():
    metadata = parse_index_metadata()
    categories = {v["category"] for v in metadata.values()}
    assert len(categories) > 1, f"Expected multiple categories, got {categories}"
    print("PASS test_parse_index_metadata_covers_multiple_categories")


def test_extract_title_strips_inline_html():
    html = '<div class="hed">Why Jennifer Garner Might<br>Like To Kick Your Ass</div>'
    soup = BeautifulSoup(html, "html.parser")
    title = extract_title(soup)
    assert "Jennifer Garner" in title, f"Title missing expected text: {title}"
    assert "<br>" not in title, f"Title still contains HTML: {title}"
    print("PASS test_extract_title_strips_inline_html")


def test_extract_dek_strips_byline():
    html = '<div class="dek">She may seem like a sweet girl from West Virginia.<br>by Peter Rubin</div>'
    soup = BeautifulSoup(html, "html.parser")
    dek = extract_dek(soup)
    assert "Peter Rubin" not in dek, f"Byline not stripped from dek: {dek}"
    assert "sweet girl" in dek, f"Dek content missing: {dek}"
    print("PASS test_extract_dek_strips_byline")


def test_convert_article_produces_valid_front_matter():
    path = Path("site_backup/writing/gqgarner.html")
    meta = {"publication": "GQ", "date": "2003-02-01", "category": "features"}
    result = convert_article(path, meta)
    assert result.startswith("---\n"), "Must start with YAML front matter"
    assert "title:" in result
    assert "publication: GQ" in result
    assert "category: features" in result
    print("PASS test_convert_article_produces_valid_front_matter")


def test_convert_article_fixes_image_paths():
    path = Path("site_backup/writing/xxljeezy.html")
    meta = {"publication": "XXL", "date": "2006-11-01", "category": "music"}
    result = convert_article(path, meta)
    assert "../images/" not in result, "Old relative image paths were not rewritten"
    print("PASS test_convert_article_fixes_image_paths")


def test_convert_article_strips_navigation():
    path = Path("site_backup/writing/gqgarner.html")
    meta = {"publication": "GQ", "date": "2003-02-01", "category": "features"}
    result = convert_article(path, meta)
    assert "navbar" not in result, "Old navigation should be stripped"
    assert "statcounter" not in result.lower(), "StatCounter script should be stripped"
    print("PASS test_convert_article_strips_navigation")


if __name__ == "__main__":
    test_parse_index_metadata_finds_known_articles()
    test_parse_index_metadata_covers_multiple_categories()
    test_extract_title_strips_inline_html()
    test_extract_dek_strips_byline()
    test_convert_article_produces_valid_front_matter()
    test_convert_article_fixes_image_paths()
    test_convert_article_strips_navigation()
    print("\nAll tests passed!")
