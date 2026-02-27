import requests

# Target URL
url = "https://movie.douban.com/top250"

# Send a basic request
response1 = requests.get(url)
# Check status code
print(f'Status Code for request without headers::{response1.status_code}')
print('-' * 50)
print(response1.text[:200])

# Send a request with headers
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
}
response2 =requests.get(url, headers=headers)
print(f'Status Code for request with headers:{response2.status_code}')
print('-' * 50)
print(response2.text[:200])