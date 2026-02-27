import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
from utils.disguise_utils import get_random_headers
from utils.mysql_helper import MysqlHelper

# Scrap Baidu Hot Search
async def scrape_baidu_hot_search(retries = 3):
    url = "https://top.baidu.com/board?tab=realtime"

    for attempt in range(retries):
        headers = get_random_headers()
        try:
            # Wait for 1-3 sec to act like human
            await asyncio.sleep(random.uniform(1,3))
            # Use aiohttp to fetch data
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = headers, timeout = aiohttp.ClientTimeout(total=10)) as response:

                    if response.status == 200:
                        print(f'Successfully fetched data on attempt {attempt + 1}')
                        # Get HTML content
                        html_content = await response.text()

                        # Parse HTML content into BeautifulSoup object
                        soup = BeautifulSoup(html_content, 'html.parser')
                        # Use CSS selector to find elements with specific tag and contents
                        items = soup.select(".category-wrap_iQLoo")
                        print(f'Found {len(items)} hot search topics.')

                        hot_search_list = []

                        # Generating rank index for each item and start count from 1
                        for rank_idx, item in enumerate(items, 1):

                            # Get hot index
                            hot_idx_el = item.select_one(".hot-index_1Bl1a")
                            hot_idx = hot_idx_el.get_text(strip=True) if hot_idx_el else '0'

                            # Get title
                            title_item_el = item.select_one(".c-single-text-ellipsis")
                            title = title_item_el.get_text(strip=True) if title_item_el else 'N/A'

                            # Get hot search link
                            link = item.select_one("a")["href"] if item.select_one("a") else 'N/A'

                            hot_search_list.append({
                                "rank_index": rank_idx,
                                "title": title,
                                "hot_index": hot_idx,
                                "link": link
                            })
                        print(f'Parsed {len(hot_search_list)} hot search topics.')
                        return hot_search_list

                    
                    elif response.status in [403, 429, 503]:
                        #    403: Forbidden
                        # 429: Too Many Requests
                        # 503: Service Unavailable
                        wait_time = (2 ** (attempt + 1)) + random.uniform(1,3)
                        print(f'Error status {response.status}. Backing off for {wait_time:.2f}s')
                        await asyncio.sleep(wait_time)
                    
                    else:
                        print(f'Unexpected status code: {response.status}')
                        return None
    
        except Exception as e:
            wait_time = (2 ** (attempt + 1)) + random.uniform(1,3)
            print(f'Error: {e}. Backing off for {wait_time:.2f}s')
            await asyncio.sleep(wait_time)
    return None

# Insert data into database
async def to_db(data_list):
    db = MysqlHelper()
    query = """
    INSERT IGNORE INTO baidu_hot_search (
        rank_index,
        title,
        hot_index,
        link,
        created_at
    ) VALUES(%s, %s, %s, %s, CURDATE())
    """

    def _insert():
        with db.transaction() as cursor:
            count = 0
            for item in data_list:
                count += cursor.execute(query, (
                    item["rank_index"],
                    item["title"],
                    item["hot_index"],
                    item["link"]
                ))
            print(f'Successfully inserted {count} hot search topics into the database.')
    result = await asyncio.to_thread(_insert)

# Main function
async def main():
    data_list = await scrape_baidu_hot_search()
    if data_list:
        print(f'Successfully scraped {len(data_list)} hot search topics.')
        await to_db(data_list)
    elif data_list is None:
        print('Failed to scrape data.')
    else:
        print('Scraping returned empty list - CSS selectors may have changed')

if __name__ == '__main__':
    asyncio.run(main())