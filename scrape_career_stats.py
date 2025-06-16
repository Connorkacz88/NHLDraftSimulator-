from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from tqdm import tqdm

# Config
YEARS = range(2024, 1999, -1)
BASE_URL = "https://www.eliteprospects.com/draft/nhl-entry-draft/{}"

country_map = {
    "1": "Sweden", "2": "Finland", "3": "Canada", "4": "Slovakia", "5": "Norway",
    "6": "United States", "7": "Denmark", "8": "Czechia", "9": "Russia", "10": "Switzerland",
    "11": "Austria", "14": "France", "19": "Italy", "21": "Germany", "23": "Belarus", "26": "Kazakhstan"
}

position_map = {
    "D": "Defenseman", "C": "Center", "RW": "Right Wing", "LW": "Left Wing", "F": "Forward"
}

all_drafts = []

def get_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector("table.table-striped.players.table-sortable.highlight-stats", timeout=15000)
        html = page.content()
        browser.close()
        return html

# Use tqdm to show progress bar over years
for year in tqdm(YEARS, desc="Scraping NHL Draft Years"):
    try:
        html = get_rendered_html(BASE_URL.format(year))
        soup = BeautifulSoup(html, "html.parser")

        # Get the specific table
        table = soup.find("table", class_="table table-striped players table-sortable highlight-stats")

        if not table:
            print(f"❌ Table not found for {year}")
            continue

        for row in table.select("tbody tr"):
            cols = row.find_all("td")
            if len(cols) < 9:
                continue

            pick = cols[0].text.strip()
            team = cols[1].text.strip()
            player_raw = cols[2].text.strip()

            # Flag nationality
            flag_img = cols[2].find("img")
            nationality = "Unknown"
            if flag_img and "src" in flag_img.attrs:
                match = re.search(r"/(\d+)\.png", flag_img["src"])
                if match:
                    nationality = country_map.get(match.group(1), "Unknown")

            # Extract position
            match = re.search(r"\((.*?)\)", player_raw)
            if match:
                raw_pos = match.group(1)
                full_pos = "/".join([position_map.get(p.strip(), p.strip()) for p in raw_pos.split("/")])
                player_name = re.sub(r"\s*\(.*?\)", "", player_raw).strip()
            else:
                full_pos = "Unknown"
                player_name = player_raw.strip()

            row_data = {
                "Year": year,
                "Pick": pick,
                "Team": team,
                "Player": player_name,
                "Position": full_pos,
                "Nationality": nationality,
                "Seasons": cols[3].text.strip(),
                "GP": cols[4].text.strip(),
                "G": cols[5].text.strip(),
                "A": cols[6].text.strip(),
                "TP": cols[7].text.strip(),
                "PIM": cols[8].text.strip()
            }

            all_drafts.append(row_data)

        time.sleep(1)  # Polite scraping

    except Exception as e:
        print(f"❌ Error scraping {year}: {e}")

# Save final DataFrame
df = pd.DataFrame(all_drafts)
output_path = "/Users/cconnorkaczmarek/Documents/DraftSimulator/Data/nhl_draft_summary_2000_2024.csv"
df.to_csv(output_path, index=False)
print(f"✅ Done. Data saved to:\n{output_path}")





