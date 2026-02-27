from fake_useragent import UserAgent

ua = UserAgent()

def get_random_headers():
    # Generate random browser-like headers
    return{
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

if __name__ =='__main__':
    print(get_random_headers())
    