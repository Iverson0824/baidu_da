import asyncio
import os
from scrapers.base_scraper import BaseScraper
import aiohttp
import random
from utils.disguise_utils import get_random_headers

class DoubanTop250(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(url="https://movie.douban.com/top250", **kwargs)
        self.cookies = {
            "bid": "R3RBiNuPDdY"
        }
        self.total_pages = 10

    def gen_urls(self):
        return [f'{self.url}?start={i * 25}' for i in range(self.total_pages)]

    async def fetch_page(self, url):
        for attempt in range(self.retries):
            headers = get_random_headers()
            try:
                await asyncio.sleep(random.uniform(3,6) if attempt == 0 else random.uniform(2,5))
                async with aiohttp.ClientSession(headers = headers, timeout = aiohttp.ClientTimeout(total = self.timeout),cookies=self.cookies) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            print(f'Successfully fetched data on attempt {attempt + 1}')
                            return await response.text()
                        elif response.status in [403, 429, 503, 418]:
                            print(f'Fetch data failed on attempt {attempt + 1}, error status: {response.status}')
                            wait_time = (2 ** (attempt + 1)) + random.uniform(1,3)
                            print(f'Waiting for {wait_time:.2f}s before next attempt')
                            await asyncio.sleep(wait_time)
                        else:
                            print(f'Fetch data failed on attempt {attempt + 1}, unexpected error status: {response.status}')
                            return None
            except Exception as e:
                print(f'Attempt {attempt + 1} failed, error type: {type(e).__name__}, error message: {e}')
                wait_time = (2 ** (attempt + 1)) + random.uniform(1,3)
                print(f'Waiting for {wait_time:.2f}s before next attempt')
                await asyncio.sleep(wait_time)
        return None

    def save_html(self,html, page_num):
        os.makedirs('data/db_top250_raw', exist_ok = True)
        with open(f'data/db_top250_raw/page_{page_num}.html', 'w', encoding = 'utf-8') as f:
            f.write(html)

    def valid_html(self, html):
        if html and 'rating_num' in html:
            print('Valid HTML content')
            return True
        else:
            print('Invalid HTML content')
            return False

    async def download_all(self):
        urls = self.gen_urls()
        for i, url in enumerate(urls):
            filepath = f'data/db_top250_raw/page_{i}.html'
            if os.path.exists(filepath) and os.path.getsize(filepath) > 50000:
                print(f'Page {i+1} already exists and is valid, skipping')
                continue
            html = await self.fetch_page(url)
            if self.valid_html(html):
                self.save_html(html, i)
                print(f'Successfully saved page {i+1}')
            else:
                print(f'Failed to save page {i+1}')
            if i < len(urls) - 1:
                await asyncio.sleep(random.uniform(5,10))
        print('All pages downloaded successfully')

if __name__ == '__main__':
    scraper = DoubanTop250()
    asyncio.run(scraper.download_all())
        