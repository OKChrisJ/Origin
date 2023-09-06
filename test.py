import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
from csv import writer
import asyncio
from tqdm import tqdm, trange

SEASONS = list(range(1981, 2024))

DATA_DIR = "testing_data_collection"
STANDINGS_DIR = os.path.join(DATA_DIR, "games")

curr_dir = './output'
indv_player_data_dir = os.path.join(curr_dir, 'indv_player_data')  # Correct directory path

if not os.path.exists(indv_player_data_dir):
    os.makedirs(indv_player_data_dir)  # Use makedirs to create intermediate directories

async def get_html(url, selector, sleep=5, retries=15, timeout=0):
    html = None
    for i in range(1, retries + 1):
        time.sleep(sleep * i)

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch()
                page = await browser.new_page()
                await page.goto(url, timeout=30000)  # if can't load page in 30s, timeout error gets thrown
                #print(url)
                html = await page.inner_html(selector, timeout=60000)  # grab all html with identifier named {selector} within 60s
                #print('got html')
        except PlaywrightTimeout:
            print(f"Timeout on {url}")
            if i == retries:  # times out for 5th time
                print('No games this month')
            continue
        else:
            break
    return html

async def get_season_tables():
    all_html_files = []
    for season in tqdm(SEASONS, desc='Seasons completed:  '):
        url = f'https://basketball.realgm.com/nba/players/{season}'
        html = await get_html(url, 'table', timeout=60000)
        all_html_files.append(html)  # No need for await here

        soup = BeautifulSoup(html, 'html.parser')  # No need for await here

        name_html = soup.find_all('td', attrs={'data-th': 'Player'})
        pos_html = soup.find_all('td', attrs={'data-th': 'Pos'})

        names = []
        positions = []

        for row in name_html:
            names.append(row.text)

        for row in pos_html:
            positions.append(row.text)

        with open(os.path.join(indv_player_data_dir, f'season_{season}_players.csv'), 'w') as f_object:
            writer_object = writer(f_object)
            assert len(names) == len(positions)
            for i in range(len(names)):
                writer_object.writerow([names[i], positions[i]])  # Corrected this line

if __name__ == "__main__":
    asyncio.run(get_season_tables())

