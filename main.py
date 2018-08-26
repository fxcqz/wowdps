import asyncio
import re
import json
import aiohttp
from time import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

CLASSES = (
    'deathknight', 'demon_hunter', 'druid', 'hunter', 'mage', 'monk', 'paladin',
    'priest', 'rogue', 'shaman', 'warlock', 'warrior',
)
all_class_data = []

stringifiers = {
    'character': lambda col: col.find_element_by_tag_name('a').get_property('href'),
    'dps': lambda col: float(col.text),
    'spec': lambda col: col.text,
    'header': lambda col: col.text.lower().replace(' ', '-'),
}

INITIAL_URL_FMT = 'https://www.wowprogress.com/simdps/?class={player_class}'
NEXT_URL_FMT = 'https://www.wowprogress.com/simdps/char_rating/next/{page}/class.{player_class}'

def get_data_from_td(header, col):
    if header not in stringifiers:
        return None
    return stringifiers[header](col)

def get_table_cols(row, tag='td', headers=None):
    def get_header(i):
        if tag == 'th':
            return 'header'
        elif headers is None:
            return None
        return headers[i]

    return list(filter(None,
        (get_data_from_td(get_header(i), col)
        for i, col in enumerate(row.find_elements_by_tag_name(tag)))
    ))

def get_table(driver, player_class, page=None):
    # when page is None, use the initial url
    if page is None:
        url = INITIAL_URL_FMT.format(**locals())
    else:
        url = NEXT_URL_FMT.format(**locals())

    driver.get(url)
    table = driver.find_element_by_css_selector('table.rating')
    rows = table.find_elements_by_tag_name('tr')
    headers = []
    data = []

    for row in rows:
        if not headers:
            headers = get_table_cols(row, 'th')[:-1] + ['dps']
            continue

        data.append(get_table_cols(row, headers=headers))

    return data

async def finalise_data(session, all_data, current_table):
    for url, spec, dps in current_table:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.read(), 'html.parser')
            ilvl_div = next((div.string for div in soup.find_all('div', class_='gearscore')
                             if div.string and div.string.startswith('Item Level')),
                            None)
            if ilvl_div:
                ilvl = float(ilvl_div.split(':')[1].strip())
                all_data.append((spec, ilvl, dps))

async def main():
    global all_class_data
    opts = Options()
    opts.set_headless(headless=True)
    driver = webdriver.Firefox(firefox_options=opts)
    async with aiohttp.ClientSession() as session:
        for class_ in CLASSES:
            print("Getting data for {}".format(class_))
            start = time()
            table = get_table(driver, class_)
            for page in range(10):
                table.extend(get_table(driver, class_, page=page))
            print("Got class data in {:.2f} sec".format(time() - start))
            asyncio.ensure_future(finalise_data(session, all_class_data, table))
            print("Waiting for 5 sec")
            await asyncio.sleep(5)
    driver.quit()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
        # always write whatever data we have got
        with open('data.json', 'w') as j:
            j.write(json.dumps(all_class_data))
