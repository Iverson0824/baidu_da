import asyncio
import aiohttp
from utils.disguise_utils import get_random_headers
from utils.proxy_mgr import get_random_proxy

async def fetch_stealth(session, url):

    # get an identity
    headers = get_random_headers()

    # get an ip
    proxy = get_random_proxy()

    # send a request with random headers and proxy
    try:
        async with session.get(url, headers=headers, timeout=10) as response:    # (, proxy=proxy) removed for now since i have no ips
            print(f'Status:{response.status}')
            if response.status == 200:
                return await response.text()
            elif response.sattus == 403:
                print('Blocked')
    except Exception as e:
        print(f'Error:{e}')

async def main():
    url = 'http://httpbin.org/get'    # A site for testing HTTP requests
    async with aiohttp.ClientSession() as session:
        html_content = await fetch_stealth(session, url)
        if html_content:
            print('Disguise success!')

if __name__ == "__main__":
    asyncio.run(main())



