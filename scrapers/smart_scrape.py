import asyncio
import aiohttp
import random
from utils.disguise_utils import get_random_headers

async def smart_fetch(session, url, retries=3):
    # Fetch a url with random headers, exponential backoff, and error handling
    for attempt in range(retries):
        headers = get_random_headers()
        try:
            
            await asyncio.sleep(random.uniform(1,3))    # Wait for 1-3 sec to act like human

            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status ==200:
                    print(f'Success on attempt{attempt + 1}')
                    return await response.text()

                elif response.status in [403, 429, 503]:
                    # 403: Forbidden
                    # 429: Too Many Requests
                    # 503: Service Unavailable
                    wait_time = (2 ** (attempt + 1)) + random.uniform(1,3)
                    print(f'Error status {response.status}. Backing off for {wait_time:.2f}s')
                    await asyncio.sleep(wait_time)
                
                else:
                    print(f'Unexpected status {response.status}')
                    break

        except Exception as e:
            wait_time = (2 ** (attempt + 1))
            print(f'Connection Error: {e}. Retrying in {wait_time:.2f}s')
            await asyncio.sleep(wait_time)
    
    return None

async def main():
    url = 'http://httpbin.org/status/429'
    print(f'Attempting to fetch {url}')
    async with aiohttp.ClientSession() as session:
        html_content = await smart_fetch(session, url)
        if not html_content:
            print('Failed to fetch the page after all retries.')

if __name__ == "__main__":
    asyncio.run(main())
                    