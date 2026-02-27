import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Build a Async scraper function
async def fetch_baidu_hot_search():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    # Open a client session
    async with aiohttp.ClientSession(headers=headers) as session:
        
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()

                #Parsing the response
                soup = BeautifulSoup(html_content, 'html.parser')
                items = soup.select(".category-wrap_iQLoo")

                hot_search_list = []

                for item in items:
                    # Get hot index
                    hot_idx = item.select_one(".hot-index_1Bl1a")
                    hot_idx = hot_idx.get_text(strip=True)

                    # Get title
                    title_item = item.select_one(".c-single-text-ellipsis")
                    title = title_item.get_text(strip=True)

                    # Get hot search link
                    link = item.select_one("a")["href"]

                    hot_search_list.append({
                        "hot_index": hot_idx,
                        "title": title,
                        "link": link
                    })
                for data in hot_search_list[0:10]:
                    print(f'Hot Index: {data["hot_index"]}\nTitle: {data["title"]}\nLink: {data["link"]}\n')

            else:
                print(f'Failed to fetch the page. Status code: {response.status}')

# The event loop is the core of async programming
# It manages and runs async tasks
if __name__ == "__main__":
    asyncio.run(fetch_baidu_hot_search())
