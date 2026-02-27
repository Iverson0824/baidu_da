import asyncio
import aiohttp
from bs4 import BeautifulSoup

sem = asyncio.Semaphore(5)

# Scrape details for a specific hot search link
async def fetch_detail(session, hot_index, title, url):
    try:
        async with session.get(url) as response:
            html_content = await response.text()
            print(f'Fetched details for {title} (hot index: {hot_index})')
            return len(html_content)
    except Exception as e:
        print(f'Failed to fetch details for {title} (hot index: {hot_index}): {e}')
        return 0

# Main function to scrape hot search details
async def main():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    # Open a client session
    async with aiohttp.ClientSession(headers=headers) as session:
        # get the list
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.select(".category-wrap_iQLoo")

        print(f'Found {len(items)} hot search items')

        # Create a list of tasks to fetch details for each hot search item
        tasks = []
        for i, item in enumerate(items):
            hot_index = item.select_one(".hot-index_1Bl1a").get_text(strip=True)
            title = item.select_one(".c-single-text-ellipsis").get_text(strip=True)
            link = item.select_one("a")["href"]

            # Call the fetch_detail function and add it to the list of tasks
            task = fetch_detail(session, hot_index, title, link)
            tasks.append(task)

        # Run all tasks concurrently
        # * unpacks the list of tasks into individual arguments
        results = await asyncio.gather(*tasks)

        # Print the results
        for i, result in enumerate(results):
            print(f'Hot index {i+1}: {result}')
        
if __name__ == "__main__":
    asyncio.run(main())

        