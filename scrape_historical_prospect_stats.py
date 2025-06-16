import time
import csv
from dataclasses import dataclass, asdict
from selectolax.parser import HTMLParser
from playwright.sync_api import sync_playwright
from tqdm import tqdm
import pandas as pd

# Pandas display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# _____________________ CONFIG _____________________
BASE_DRAFT_URL = 'https://www.eliteprospects.com/draft/nhl-entry-draft/'

@dataclass
class Prospect:
    name: str | None
    nationality: str | None
    position: str | None
    height: str | None
    weight: str | None
    shoots: str | None
    team_drafted: str | None
    draft_year_team: str | None
    draft_year_team_league: str | None
    gp: str | None
    g: str | None
    a: str | None
    tp: str | None
    pim: str | None
    plus_minus: str | None

# _____________________ PLAYWRIGHT SETUP _____________________
def get_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=120000 )
        page.wait_for_timeout(3000)  # wait 5 seconds for JS to load
        html = page.content()
        browser.close()
    return html

# _____________________ HELPERS _____________________
def season_string(draft_year):
    prev = str(draft_year - 1)
    curr = str(draft_year % 100).zfill(2)
    return f"{prev}-{curr}"

# _____________________ SCRAPING FUNCTIONS _____________________
def extract_player_name(html):
    h1 = html.css_first("h1.Profile_headerMain__WPgYE")
    return h1.text().strip() if h1 else None

def extract_nationality(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Nation":
            nation_link = li.css_first('a.TextLink_link__RhSiC')
            return nation_link.text().strip() if nation_link else None
    return None

def extract_position(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Position":
            return li.text().replace("Position", "").strip()
    return None

def extract_height(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Height":
            return li.text().replace("Height", "").strip()
    return None

def extract_weight(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Weight":
            return li.text().replace("Weight", "").strip()
    return None

def extract_shoots(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Shoots":
            return li.text().replace("Shoots", "").strip()
    return None

def extract_team_drafted(html):
    for li in html.css('li'):
        label = li.css_first('span.PlayerFacts_factLabel__EqzO5')
        if label and label.text().strip() == "Drafted":
            link = li.css_first('a.TextLink_link__RhSiC')
            return link.text().strip() if link else None
    return None

def extract_draft_year_team(html, season):
    section = html.css_first('section#player-statistics')
    if not section:
        return None

    rows = section.css('table tr')
    for row in rows:
        spans = row.css('span')
        for span in spans:
            span_text = span.text().strip()
            span_class = span.attributes.get('class')
            if span_class and 'PlayerStatistics_season__' in span_class:
                if span_text == season:
                    team_cell = row.css_first('td.PlayerStatistics_teamName__6pQiz a.TextLink_link__RhSiC')
                    if team_cell:
                        return team_cell.text().strip()
    return None

def extract_draft_year_league(html, season):
    section = html.css_first('section#player-statistics')
    if not section:
        return None

    rows = section.css('table tr')
    for row in rows:
        spans = row.css('span')
        for span in spans:
            span_text = span.text().strip()
            span_class = span.attributes.get('class')
            if span_class and 'PlayerStatistics_season__' in span_class:
                if span_text == season:
                    cells = row.css('td')
                    if len(cells) > 2:
                        league_link = cells[2].css_first('a.TextLink_link__RhSiC')
                        if league_link:
                            return league_link.text().strip()
    return None

def extract_draft_year_stats(html, season):
    section = html.css_first('section#player-statistics')
    if not section:
        return None
    rows = section.css('table tr')
    for row in rows:
        spans = row.css('span')
        for span in spans:
            span_text = span.text().strip()
            span_class = span.attributes.get('class')
            if span_class and 'PlayerStatistics_season__' in span_class:
                if span_text == season:
                    cells = row.css('td')
                    stats = {
                        'gp': cells[3].text().strip() if len(cells) > 3 else None,
                        'g': cells[4].text().strip() if len(cells) > 4 else None,
                        'a': cells[5].text().strip() if len(cells) > 5 else None,
                        'tp': cells[6].text().strip() if len(cells) > 6 else None,
                        'pim': cells[7].text().strip() if len(cells) > 7 else None,
                        'plus_minus': cells[8].text().strip() if len(cells) > 8 else None
                    }
                    return stats
    return None

# _____________________ PARSE PAGES _____________________
def parse_prospect_page(html_text, draft_year):
    html = HTMLParser(html_text)
    season = season_string(draft_year)
    stats = extract_draft_year_stats(html, season)
    team = extract_draft_year_team(html, season)
    league = extract_draft_year_league(html, season)

    return Prospect(
        name = extract_player_name(html),
        nationality = extract_nationality(html),
        position = extract_position(html),
        height = extract_height(html),
        weight = extract_weight(html),
        shoots = extract_shoots(html),
        team_drafted = extract_team_drafted(html),
        draft_year_team = team,
        draft_year_team_league = league,
        gp = stats.get('gp') if stats else None,
        g = stats.get('g') if stats else None,
        a = stats.get('a') if stats else None,
        tp = stats.get('tp') if stats else None,
        pim = stats.get('pim') if stats else None,
        plus_minus = stats.get('plus_minus') if stats else None
    )

def get_prospect_links(draft_year):
    draft_url = f"{BASE_DRAFT_URL}{draft_year}"
    html_text = get_rendered_html(draft_url)
    html = HTMLParser(html_text)
    players = html.css('div#drafted-players tbody tr')
    links = []
    for player in players:
        a_nodes = player.css('a')
        if len(a_nodes) >= 3:
            href = a_nodes[2].attributes.get('href')
            if href.startswith('http'):
                links.append(href)
            else:
                links.append('https://www.eliteprospects.com' + href)
    return links

# _____________________ MAIN _____________________
def main():
    all_prospects = []

    for draft_year in range(2024, 1999, -1):  # From 2024 down to 2000
        print(f'\n[INFO] Processing draft year {draft_year}')
        prospects = []
        prospect_urls = get_prospect_links(draft_year)

        for idx, url in enumerate(tqdm(prospect_urls, desc=f'Draft {draft_year}', unit='player')):
            try:
                html_text = get_rendered_html(url)
                prospect = parse_prospect_page(html_text, draft_year)
                prospects.append(prospect)
                time.sleep(0.05)  # polite delay
            except Exception as e:
                print(f'[ERROR] Failed to process {url}: {e}')

        print(f'[INFO] Fetched {len(prospects)} prospects for draft year {draft_year}')
        all_prospects.extend(prospects)

    print(f'\n[INFO] Total collected prospects across all years: {len(all_prospects)}')

    # Convert to pandas DataFrame
    df = pd.DataFrame([asdict(p) for p in all_prospects])

    # Print the DataFrame
    print(df)

    # Save to CSV
    csv_filename = 'nhl_draft_prospects_2000_to_2024.csv'
    df.to_csv(csv_filename, index=False)
    print(f'[INFO] Saved combined DataFrame to {csv_filename}')

if __name__ == '__main__':
    main()











