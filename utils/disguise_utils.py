from fake_useragent import UserAgent
class DisguiseUtils:
    def __init__(self):
        self.ua = UserAgent()
    
    def get_random_headers(self):
        # Generate random browser-like headers
        return{
        "User-Agent": self.ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

# Backward compatibility
_default_disguise_utils = DisguiseUtils()
get_random_headers = _default_disguise_utils.get_random_headers