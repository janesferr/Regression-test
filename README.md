# Visual Regression Test – README

This repo/script runs a **visual regression test** between a **source (production) website** and a **target (staging) website** by:

* Pulling URLs from each site’s **XML sitemap**
* Visiting matching paths with **Selenium (Chrome)**
* Capturing **full-page screenshots** for each page on both environments
* Producing an **HTML report** to review screenshots side-by-side

---

## What it tests

* **Source site:** `https://bumperdocbrooklyn.com`
* **Target site:** `https://staging2.bumperdocbrooklyn.com`

It fetches:

* `https://bumperdocbrooklyn.com/page-sitemap.xml`
* `https://staging2.bumperdocbrooklyn.com/page-sitemap.xml`

Then it compares pages by **path** (example: `/about/` on both sites).

---

## Output

All output is written to:

`regression_report_bumperdoc/`

Inside you’ll get:

* `index.html` – the visual report (side-by-side images per page)
* `logs.txt` – run logs
* One folder per page slug, containing:

  * `source.png`
  * `target.png`

Example:

```
regression_report_bumperdoc/
  index.html
  logs.txt
  about/
    source.png
    target.png
  contact/
    source.png
    target.png
```

---

## Requirements

### Python

* Python **3.9+** recommended

### System dependencies

* Google Chrome installed (the script uses Chrome + webdriver_manager)

---

## Install

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell
```

Install dependencies:

```bash
pip install selenium webdriver-manager requests beautifulsoup4 lxml
```

> Note: `lxml` is required because the sitemap is parsed using `lxml-xml`.

---

## Run

From the folder containing the script:

```bash
python regression_test.py
```

When finished, open the report:

* Open `regression_report_bumperdoc/index.html` in your browser

---

## How it works (high level)

1. **Fetch sitemaps** for source and target
2. Build a map of `path -> full URL` for each environment
3. Create a union of all paths and loop through each page
4. For each page:

   * Load with Selenium
   * Attempt to dismiss cookie banners (best-effort)
   * Scroll to trigger lazy-loading
   * Capture a **full-page screenshot** using Chrome DevTools Protocol
5. Generate `index.html` to review results manually

---

## Configuration

At the top of the script:

```python
SOURCE_SITE = "https://bumperdocbrooklyn.com"
TARGET_SITE = "https://staging2.bumperdocbrooklyn.com"
REPORT_DIR = "regression_report_bumperdoc"
HEADLESS = True
RETRY_COUNT = 2
```

### Common tweaks

* Run with a visible browser:

  * `HEADLESS = False`
* Increase retry attempts if pages are slow:

  * `RETRY_COUNT = 3` (or more)
* Change sitemap path if your site uses a different sitemap:

  * `SOURCE_SITEMAP_URL = f"{SOURCE_SITE}/page-sitemap.xml"`

---

## Notes / Behavior

* **Target sitemap fallback:** If the staging sitemap fails, the script falls back to testing only the staging homepage.
* **SSL verification disabled for sitemap requests** (`verify=False`) to avoid certificate issues in staging environments.
* **Screenshots are not pixel-diffed** automatically — this is a manual review workflow using side-by-side images.
* A simple **Pass / Fail checkbox** UI is included in the report, but it does not persist (no backend).

---

## Troubleshooting

### 403 / bot blocking

The script sets a custom user-agent and disables some automation flags, but if you still see blocks:

* Try `HEADLESS = False`
* Ensure your environment allows automated browsing
* Consider allowinglist rules on staging (if applicable)

### Selenium/Chrome issues

* Update Chrome
* Reinstall dependencies
* Ensure no corporate policies block WebDriver

### Sitemap returns 0 URLs

* Confirm the sitemap URL is accessible in a browser
* Confirm it contains `<loc>` entries

---

## Suggested improvements (optional)

If you want to level this up:

* Add **image diffing** (Pillow + pixelmatch-like logic) and highlight changes
* Add filtering (only certain paths)
* Save Pass/Fail annotations to a JSON file
* Parallelize page runs for speed (with separate browser instances)

---

## License

Internal/Project use (add your preferred license here).
