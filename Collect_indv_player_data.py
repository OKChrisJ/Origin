import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from zipfile import ZipFile
import time
from csv import writer, reader
from decimal import *
import pandas as pd

SEASONS = list(range(1980, 2024))
months = ['november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']

DATA_DIR = "testing_data_collection"
STANDINGS_DIR = os.path.join(DATA_DIR, "games")
curr_dir = '/Users/chrisjeff/Desktop/Origin'
#SCORES_DIR = os.path.join(DATA_DIR, "scores")



#get html function
async def get_html(url, selector, sleep=5, retries=15, timeout=0):
  html = None
  for i in range(1, retries+1):
    time.sleep(sleep * i)

    try:
      async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=30000) #if can't load page in 30s, timeout error gets thrown
        print(url)
        html = await page.inner_html(selector,timeout=60000) #grab all html with identifier named {selector} within 60s
        print('got html')
    except PlaywrightTimeout:
      print(f"Timeout on {url}")
      if i == retries: #timesout for 5th time
        print('No games this month')
      continue
    else:
      break
  return html





async def get_season_tables():
  all_html_files = []
  for season in SEASONS:
    url = f'https://basketball.realgm.com/nba/players/{season}'
    html = await get_html(url, 'table', timeout=60000)
    await all_html_files.append(html)
    print(f'collected data from season {season}')

    soup = await BeautifulSoup(html, 'html.parser')

    name_html = soup.find_all('td', attrs={'data-th': 'Player'})
    pos_html = soup.find_all('td', attrs={'data-th': 'Pos'})

    names = []
    positions = []

    for row in name_html:
      names.append(row.text)

    for row in pos_html:
      positions.append(row.text)



    with open(f'{curr_dir}/indv_player_data/season_{season}_players.csv', 'w') as f_object:
      writer_object = writer(f_object)
      assert len(names) == len(positions)
      for i in range(len(names)):
        writer_object.writerow(names[i], positions[i])
      f_object.close()


  await get_season_tables()