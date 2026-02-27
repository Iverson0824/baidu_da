import random

# In real world, the proxy list would be provided by a proxy service
# Or a database of proxies i've found/bought
proxies = [
    "http://123.45.67.89:8080",
    "http://98.76.54.32:3128",
    "http://55.66.77.88:1080"
]

def get_random_proxy():
    return random.choice(proxies)

if __name__ == "__main__":
    print(f'current proxy:{get_random_proxy()}')