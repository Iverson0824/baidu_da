import pytest
from scrapers.baidu_pipe import BaiduHotSearchScraper

class TestBaiduHotSearchScraper:

    def test_inherits_from_base_scraper(self):
        from scrapers.base_scraper import BaseScraper
        scraper = BaiduHotSearchScraper()
        assert isinstance(scraper, BaseScraper)

    def test_url_is_set(self):
        scraper = BaiduHotSearchScraper()
        assert scraper.url == "https://top.baidu.com/board?tab=realtime"
    
    def test_parse_with_sample_html(self):
        scraper = BaiduHotSearchScraper()
        html = """
        <html>
            <body>
                <div class="category-wrap_iQLoo">
                    <div class="hot-index_1Bl1a">1</div>
                    <div class="c-single-text-ellipsis">Test Title</div>
                    <a href="https://www.baidu.com">Test Link</a>
                </div>
            </body>
        </html>
        """
        result = scraper.parse(html)
        assert result == [
            {
                "rank_index": 1,
                "title": "Test Title",
                "hot_index": "1",
                "link": "https://www.baidu.com"
            }
        ]
    @pytest.mark.asyncio
    async def test_fetch_success(self):
        scraper = BaiduHotSearchScraper()
        html = await scraper.fetch()
        assert html is not None
        assert len(html) > 0
    
    @pytest.mark.asyncio
    async def test_fetch_failure(self):
        scraper = BaiduHotSearchScraper(retries = 1, timeout = 1)
        html = await scraper.fetch()
        assert html is None