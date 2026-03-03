import asyncio
import aiohttp
import random
from utils.disguise_utils import get_random_headers

class BaseScraper:

    def __init__(self, url, retries = 5, timeout = 10):
        # store the 3 values onto self
        self.url = url
        self.retries = retries
        self.timeout = timeout
    
    async def fetch(self):

        for attempt in range(self.retries):
            headers = get_random_headers()
            try:
                await asyncio.sleep(random.uniform(3,6) if attempt == 0 else random.uniform(2,5))
                async with aiohttp.ClientSession(headers = headers, timeout = aiohttp.ClientTimeout(total = self.timeout)) as session:
                    async with session.get(self.url) as response:
                        if response.status == 200:
                            print(f'Successfully fetched data on attempt {attempt + 1}')
                            return await response.text()
                        elif response.status in [403, 429, 503]:
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

    def parse(self, html):
        raise NotImplementedError('Subclasses must implement the parse method')
    
    async def run(self):
        html = await self.fetch()
        if html:
            return self.parse(html)
        else:
            print(f'No HTML content fetched, cannot parse.')
            return None

