# SELENIUM VERSION WITH IMPROVED RENDERING FOR SITE-A

import os

import time

import requests

import logging

from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path

from urllib.parse import urlparse

import base64

 

# ///

import os

os.environ['WDM_SSL_VERIFY'] = '0'  # disables SSL verification in webdriver-manager

 

from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

 

options = Options()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36'
)


# === CONFIGURATION ===

SOURCE_SITE = "https://bumperdocbrooklyn.com"

TARGET_SITE = "https://staging2.bumperdocbrooklyn.com"


SOURCE_SITEMAP_URL = f"{SOURCE_SITE}/page-sitemap.xml"

TARGET_SITEMAP_URL = f"{TARGET_SITE}/page-sitemap.xml"

REPORT_DIR = "regression_reportforbumperdoc2"

HEADLESS = True

 

# === LOGGING SETUP ===

os.makedirs(REPORT_DIR, exist_ok=True)

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s [%(levelname)s] %(message)s",

    handlers=[

        logging.FileHandler(os.path.join(REPORT_DIR, "logs.txt")),

        logging.StreamHandler()

    ]

)

 

# === SETUP SELENIUM ===

logging.info("Initializing Chrome WebDriver")

options = Options()

if HEADLESS:

    options.add_argument('--headless=new')

options.add_argument('--start-maximized')

options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.maximize_window()

 

# === UTILITY FUNCTIONS ===

def get_sitemap_urls(sitemap_url):

    logging.info(f"Fetching sitemap: {sitemap_url}")

    try:

        # response = requests.get(sitemap_url, verify="/selenium-regression/zscaler_cert.pem")

        response = requests.get(sitemap_url, verify=False)

        response.raise_for_status()

        # soup = BeautifulSoup(response.content, 'xml')
        soup = BeautifulSoup(response.content, "lxml-xml")

        urls = [loc.text.strip() for loc in soup.find_all("loc")]

        logging.info(f"Found {len(urls)} URLs")

        return urls

    except Exception as e:

        logging.error(f"Error fetching sitemap from {sitemap_url}: {e}")

        return []

 

def get_path_slug(path):

    return path.strip('/').replace('/', '_') or 'home'




import base64  # Make sure this is imported at the top if not already

 

def take_fullpage_screenshot(url, output_path):

    try:

        logging.info(f"Navigating to {url}")

        driver.get(url)

        time.sleep(3)

 

        # Dismiss cookie banner if present

        try:

            accept_button = driver.find_element("xpath", "//button[contains(text(), 'Accept')]")

            accept_button.click()

            logging.info("Cookie banner dismissed.")

            time.sleep(1)

        except Exception:

            logging.info("No cookie banner found.")

 

        # Trigger lazy loading by scrolling

        total_height = driver.execute_script("return document.body.scrollHeight")

        for y in range(0, total_height, 500):

            driver.execute_script(f"window.scrollTo(0, {y})")

            time.sleep(0.2)

 

        # 🔁 Return to top to reset sticky headers or banners

        driver.execute_script("window.scrollTo(0, 0)")

        time.sleep(0.5)

 

        # Optional: Trigger layout reflow to fix visual glitches

        driver.execute_script("window.dispatchEvent(new Event('resize'))")

        time.sleep(0.5)

 

        # 📸 Use CDP to capture full-page screenshot

        screenshot = driver.execute_cdp_cmd("Page.captureScreenshot", {

            "format": "png",

            "captureBeyondViewport": True,

            "fromSurface": True

        })

 

        # 💾 Save screenshot

        with open(output_path, "wb") as f:

            f.write(base64.b64decode(screenshot["data"]))

 

        logging.info(f"Saved screenshot: {output_path}")

        return True

 

    except Exception as e:

        logging.error(f"Failed to capture screenshot for {url}: {e}")

        return False





# === MAIN LOGIC ===

def run_test():

    logging.info("Starting regression test")

 

    source_urls = get_sitemap_urls(SOURCE_SITEMAP_URL)

    target_urls = get_sitemap_urls(TARGET_SITEMAP_URL)

 

    source_map = {urlparse(u).path: u for u in source_urls}

    target_map = {urlparse(u).path: u for u in target_urls}

 

    all_paths = sorted(set(source_map.keys()).union(set(target_map.keys())))

    report_entries = []

 

    for path in all_paths:

        slug = get_path_slug(path)

        page_dir = os.path.join(REPORT_DIR, slug)

        os.makedirs(page_dir, exist_ok=True)

 

        source_img = os.path.join(page_dir, "source.png")

        target_img = os.path.join(page_dir, "target.png")

 

        src_url = source_map.get(path)

        tgt_url = target_map.get(path)

 

        logging.info(f"Comparing {src_url or '[missing source]'} to {tgt_url or '[missing target]'}")

 

        source_success = False

        target_success = False

 

        if src_url:

            source_success = take_fullpage_screenshot(src_url, source_img)

        else:

            logging.warning(f"Path not in source: {path}")

 

        if tgt_url:

            target_success = take_fullpage_screenshot(tgt_url, target_img)

        else:

            logging.warning(f"Path not in target: {path}")

 

        report_entries.append({

            "slug": slug,

            "path": path,

            "source": f"{slug}/source.png" if source_success else None,

            "target": f"{slug}/target.png" if target_success else None,

            "source_failed": not source_success,

            "target_failed": not target_success

        })

 

    generate_html_report(report_entries)

 

# === REPORT GENERATION ===

def generate_html_report(entries):

    logging.info("Generating HTML report")

    html = ["<html><head><title>Regression Report</title>",

            "<style>body{font-family:sans-serif}img{max-width:45%;border:1px solid #ccc;margin:10px}div.page{margin-bottom:40px;}label{margin-right:20px} .missing{color:red;}</style>",

            "</head><body>",

            "<h1>Visual Regression Report</h1>"]

 

    for entry in entries:

        html.append(f"<div class='page'><h2>{entry['path']}</h2>")

        html.append("<div><label><input type='checkbox'/> Pass</label><label><input type='checkbox'/> Fail</label></div>")

 

        if entry['source']:

            html.append(f"<img src='{entry['source']}' alt='Source'>")

        else:

            html.append("<p class='missing'>❌ Source page not available</p>")

 

        if entry['target']:

            html.append(f"<img src='{entry['target']}' alt='Target'>")

        else:

            html.append("<p class='missing'>❌ Target page not available</p>")

 

        html.append("</div>")

 

    html.append("</body></html>")

 

    try:

        with open(os.path.join(REPORT_DIR, "index.html"), "w", encoding="utf-8") as f:

            f.write('\n'.join(html))

        logging.info(f"✅ HTML report generated: {REPORT_DIR}/index.html")

    except Exception as e:

        logging.error(f"Failed to generate HTML report: {e}")

 

# === EXECUTION ===

try:

    run_test()

except Exception as e:

    logging.exception(f"Unexpected error during execution: {e}")

finally:

    driver.quit()

    logging.info("WebDriver closed")