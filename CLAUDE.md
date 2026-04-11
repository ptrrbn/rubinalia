# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ruby environment

rbenv manages Ruby (3.2.0). Any shell session that runs `bundle` or `jekyll` must load rbenv shims first — the system Ruby (2.6) will not work:

```bash
export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH" && eval "$(rbenv init -)"
```

## Common commands

```bash
# Build the site
bundle exec jekyll build

# Local preview (http://localhost:4000)
bundle exec jekyll serve

# Run conversion script tests
python3 scripts/test_convert.py

# Run html-proofer (after build)
bundle exec htmlproofer _site --disable-external --ignore-missing-alt
```

## Architecture

A Jekyll static site with a single `_writing` collection (~37 articles). No theme — three hand-built layouts.

**Content pipeline:** Source articles in `site_backup/writing/` (not committed, local archive only) were converted to Jekyll collection items via `scripts/convert_articles.py`. That script is one-time-use and already ran; `_writing/` contains the output. Do not re-run the script without backing up `_writing/` first.

**URL structure:**
- `/` — writing index (`index.html`), articles grouped by category via Liquid loop
- `/writing/:slug/` — individual articles (layout: `article.html` → `default.html`)
- `/about/` — about page (`about.html`)

**Asset paths** use Jekyll's `relative_url` filter in layouts/pages (e.g. `{{ '/assets/css/main.css' | relative_url }}`). Article body HTML uses hardcoded `/assets/images/...` paths — these work correctly when `baseurl: ""` (custom domain). If `baseurl` is ever changed (e.g. for subdirectory testing), article images will break.

**Categories** must be one of: `features`, `music`, `film`, `crit`, `other`.

## Deployment

Cloudflare Pages auto-deploys from `main` at `rubinalia.com`. Every push to `main` triggers a rebuild. Build command: `bundle config set --local without 'development test' && bundle install && bundle exec jekyll build`. Output directory: `_site`. `_config.yml` has `baseurl: ""` — keep it that way.

## What's intentionally excluded

- `site_backup/` — full FTP backup of the old site (675MB), local archive only, gitignored
- `docs/` — design spec and implementation plan, gitignored
- WordPress blog ("Boggler Redux") — not migrated, SQL dumps are gitignored
- Personal photo galleries and travel pages — preserved in `site_backup/` only
