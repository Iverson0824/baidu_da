import pytest
from scrapers.base_scraper import BaseScraper

class TestBaseScraper:
    def test_init_stores_attributes(self):
        scraper = BaseScraper("https://www.baidu.com", retries = 5, timeout = 10)
        assert scraper.url == "https://www.baidu.com"
        assert scraper.retries == 5
        assert scraper.timeout == 10

    def test_parse_raises_not_implemented(self):
        scraper = BaseScraper("https://www.baidu.com")
        with pytest.raises(NotImplementedError):
            scraper.parse("<html></html>")
    
    def test_default_values(self):
        scraper = BaseScraper("https://www.baidu.com")
        assert scraper.retries == 5
        assert scraper.timeout == 10
    
    @pytest.mark.asyncio
    async def test_fetch_success(self):
        scraper = BaseScraper("https://www.baidu.com")
        html = await scraper.fetch()
        assert html is not None
        assert len(html) > 0
    
    @pytest.mark.asyncio
    async def test_fetch_failure(self):
        scraper = BaseScraper("http://192.0.2.1", retries = 1, timeout = 1)
        html = await scraper.fetch()
        assert html is None