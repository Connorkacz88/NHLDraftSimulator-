import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

pd.set_option('display.max_columns', None)
# URL to scrape
prospects_stats_url = "https://www.eliteprospects.com/draft-center#players"
response = requests.get(prospects_stats_url)
stats_doc = BeautifulSoup(response.text, "html.parser")

# Country flag number to country name
country_map = {
    "1": "Sweden",
    "2": "Finland",
    "3": "Canada",
    "4": "Slovakia",
    "5": "Norway",
    "6": "United States",
    "7": "Denmark",
    "8": "Czechia",
    "9": "Russia",
    "10": "Switzerland",
    "11": "Austria",
    "14": "France",
    "19": "Italy",
    "21": "Germany",
    "23": "Belarus",
    "26": "Kazakhstan"
}

# Position abbreviation to full name
position_map = {
    "D": "Defenseman",
    "C": "Center",
    "RW": "Right Wing",
    "LW": "Left Wing"
}

# Find the table
table = stats_doc.find("table", class_="table table-striped players table-sortable highlight-stats")

if table:
    headers = [header.text.strip() for header in table.find_all("th")]

    rows = []
    for row in table.find_all("tr")[2:]:
        cells = row.find_all("td")
        if not cells:
            continue

        row_data = []
        for i, cell in enumerate(cells):
            if i == 1:  # Nationality flag column
                img = cell.find("img")
                if img and "src" in img.attrs:
                    match = re.search(r"/(\d+)\.png", img["src"])
                    if match:
                        country_id = match.group(1)
                        country = country_map.get(country_id, "Unknown")
                        row_data.append(country)
                    else:
                        row_data.append("Unknown")
                else:
                    row_data.append("Unknown")
            else:
                row_data.append(cell.text.strip())

        rows.append(row_data)

    if rows:
        # Create DataFrame
        prospect_stats = pd.DataFrame(rows, columns=headers)
        # Strip extra spaces in column names
        prospect_stats.columns = prospect_stats.columns.str.strip()
        # Drop 'R' column if present
        if 'R' in prospect_stats.columns:
            prospect_stats.drop(columns=['R'], inplace=True)

        # Initialize position and cleaned name lists
        positions = []
        cleaned_players = []

        for player in prospect_stats['Player']:
            if isinstance(player, str):
                match = re.search(r"\((.*?)\)", player)
                if match:
                    pos_abbr = match.group(1)  # e.g., "D" or "C/LW"
                    pos_full = []

                    for part in pos_abbr.split('/'):
                        part = part.strip()
                        full = position_map.get(part, part)  # fallback if unknown
                        pos_full.append(full)

                    positions.append("/".join(pos_full))
                    cleaned_player = re.sub(r"\s*\(.*?\)", "", player).strip()
                    cleaned_players.append(cleaned_player)
                else:
                    positions.append("Unknown")
                    cleaned_players.append(player)
            else:
                positions.append("Unknown")
                cleaned_players.append("Unknown")

        # Update DataFrame with cleaned Player and new Position column
        prospect_stats['Player'] = cleaned_players
        prospect_stats['Position'] = positions

        # Output result
        prospect_stats = prospect_stats[
            ['Player', 'Position'] + [col for col in prospect_stats.columns if col not in ['Player', 'Position']]]

        print(prospect_stats)

        # Save to CSV
        prospect_stats.to_csv('/Users/cconnorkaczmarek/Documents/DraftSimulator/Data/2025_prospects_stats.csv', index=False)
        print("Data saved to 2025_prospects_stats.csv")
    else:
        print("No data found in the table.")
else:
    print("Table not found on the webpage.")













