import random

# In real world, the proxy list would be provided by a proxy service
# Or a database of proxies i've found/bought
class ProxyMgr:
    def __init__(self):
        self.proxies = [
            "http://123.45.67.89:8080",
            "http://98.76.54.32:3128",
            "http://55.66.77.88:1080"
        ]
    
    def get_random_proxy(self):
        return random.choice(self.proxies)

# Backward compatibility
_default_proxy_mgr = ProxyMgr()
get_random_proxy = _default_proxy_mgr.get_random_proxy