import time
from pathlib import Path

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv(Path(__file__).with_name('.env'))

from db import upsert_league_schedule

# --- Configuration ---
SCHEDULE_URL = "https://udisc.com/leagues/breaking-chains-sober-sundays-t0YwuH/schedule"
LINK_SUFFIX = "/leaderboard?round=1&view=scores"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

def get_upcoming_links():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(options=chrome_options)
    upcoming_urls = []

    try:
        print("🚀 Opening UDisc Schedule with Selenium...")
        driver.get(SCHEDULE_URL)

        # Wait for the dynamic list to appear
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3) # Wait for JS to render the "Upcoming" section

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        is_upcoming_zone = False
        # Scan elements to find links specifically in the Upcoming section
        for element in soup.find_all(['h2', 'h3', 'div', 'a']):
            text = element.get_text(strip=True)

            # Identify the start of the Upcoming section
            if "Upcoming" in text and len(text) < 15:
                is_upcoming_zone = True
                continue

            # Identify the end of the section
            if "Past" in text and len(text) < 15:
                is_upcoming_zone = False
                if upcoming_urls: break # Stop if we've already collected the upcoming links

            if is_upcoming_zone and element.name == 'a' and '/events/' in element.get('href', ''):
                href = element['href']
                full_url = href if href.startswith('http') else f"https://udisc.com{href}"
                score_url = full_url + LINK_SUFFIX
                if score_url not in upcoming_urls:
                    upcoming_urls.append(score_url)

    finally:
        driver.quit()
    return upcoming_urls

def get_date_from_time_tag(url):
    """Targets the <time dateTime="..."> tag directly using requests."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return f"Error {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Target the specific <time> tag
        time_tag = soup.find('time', datetime=True)

        if time_tag:
            raw_date = time_tag['datetime'] # e.g., "2026-02-08T14:00:00Z"
            # Format the ISO string to a clean YYYY-MM-DD
            dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')

    except Exception as e:
        return f"Failed: {str(e)[:15]}"
    return "Time tag not found"

# --- Main Execution ---
if __name__ == "__main__":
    links = get_upcoming_links()

    if not links:
        print("❌ No upcoming events found. Ensure the 'Upcoming' text is visible on the page.")
    else:
        print(f"✅ Found {len(links)} upcoming events. Extracting dates via <time> tags...\n")
        print(f"{'DATE':<15} | {'SCOREBOARD LINK'}")
        print("-" * 75)

        # --- NEW CODE STARTS HERE ---
        # 1. Create the list to hold the data for the DB
        upcoming_data = []

        for link in links:
            precise_date = get_date_from_time_tag(link)
            print(f"{precise_date:<15} | {link}")

            # 2. Add to our list only if we got a valid date
            if len(precise_date) == 10: # Checks for YYYY-MM-DD format
                upcoming_data.append({
                    "date": precise_date,
                    "link": link
                })

            time.sleep(0.5)

        # 3. Now send the whole list to your db.py function
        if upcoming_data:
            print(f"\n💾 Syncing {len(upcoming_data)} events to MySQL...")
            success, err = upsert_league_schedule(upcoming_data)
            if success:
                print("✨ Database update complete.")
            else:
                print(f"❌ Database error: {err}")