import requests
from bs4 import BeautifulSoup

# Get url for Baidu's hot search
url="https://top.baidu.com/board?tab=realtime"

# Set headers to mimic a browser instead of python script
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
}

# Get the HTML
response = requests.get(url, headers=headers)
html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, "html.parser")

# Use CSS selector to find elements with spcific tag and contents
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
