import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
from utils.disguise_utils import get_random_headers
from utils.mysql_helper import MysqlHelper
from scrapers.base_scraper import BaseScraper

class BaiduHotSearchScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(url = "https://top.baidu.com/board?tab=realtime", **kwargs)

    def parse(self, html):
        # Parse HTML content into BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')
        # Use CSS selector to find elements with specific tag and contents
        items = soup.select(".category-wrap_iQLoo")
        if not items:
            # Use mobile version
            items = soup.select(".c-text-item")
            print(f'Found {len(items)} hot search topics.')

            hot_search_list = []

            # Generating rank index for each item and start count from 1
            for rank_idx, item in enumerate(items, 1):

                # Get hot index
                hot_idx_el = item.select_one(".hot-index_1Bl1a")
                hot_idx = hot_idx_el.get_text(strip=True) if hot_idx_el else '0'

                # Get title
                title_item_el = item.select_one(".item-word")
                title = title_item_el.get_text(strip=True) if title_item_el else 'N/A'

                # Get hot search link
                link = item.get("href", "N/A")

                hot_search_list.append({
                    "rank_index": rank_idx,
                    "title": title,
                    "hot_index": hot_idx,
                    "link": link
                })
            print(f'Parsed {len(hot_search_list)} hot search topics.')
            return hot_search_list

        else:
            # Use desktop version
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

    async def to_db(self, data_list):
        # Create a MySQL connection
        mysql_helper = MysqlHelper()
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
            with mysql_helper.transaction() as cursor:
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
    scraper = BaiduHotSearchScraper()
    data_list = await scraper.run()
    if data_list:
        print(f'Successfully scraped {len(data_list)} hot search topics.')
        await scraper.to_db(data_list)
    elif data_list is None:
        print('Failed to scrape data.')
    else:
        print('Scraping returned empty list - CSS selectors may have changed')

if __name__ == '__main__':
    asyncio.run(main())