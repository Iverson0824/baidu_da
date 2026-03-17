import os
import re
import time
import random
from playwright.sync_api import sync_playwright
from utils.mysql_helper import MysqlHelper


class DoubanDetailScraper:
    def __init__(self, data_dir='data/db_detail_raw'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def get_movie_urls(self):
        """
        Fetch all movie (id, link) pairs from the database.
        """
        db = MysqlHelper()
        rows = db.select_all(
            'SELECT id, link FROM douban_top250 ORDER BY rank_idx'
        )
        return [(row['id'], row['link']) for row in rows]

    def extract_subject_id(self, url):
        match = re.search(r'/subject/(\d+)', url)
        return match.group(1) if match else None

    def save_html(self, subject_id, html):
        filepath = os.path.join(self.data_dir, f'{subject_id}.html')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    def is_already_scraped(self, subject_id):
        """Skip if we already have a valid HTML file (> 10KB)."""
        filepath = os.path.join(self.data_dir, f'{subject_id}.html')
        return os.path.exists(filepath) and os.path.getsize(filepath) > 10000

    def scrape_all(self):
        """
        Scrape all detail pages using Playwright.
        Saves raw HTML to data/db_detail_raw/{subject_id}.html
        """
        movie_urls = self.get_movie_urls()
        print(f'Found {len(movie_urls)} movies to scrape')

        # Count how many already done
        already_done = sum(
            1 for _, url in movie_urls
            if self.is_already_scraped(self.extract_subject_id(url))
        )
        print(f'Already scraped: {already_done}, remaining: {len(movie_urls) - already_done}')

        if already_done == len(movie_urls):
            print('All pages already scraped!')
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for i, (movie_id, url) in enumerate(movie_urls):
                subject_id = self.extract_subject_id(url)
                if not subject_id:
                    print(f'[{i+1}/{len(movie_urls)}] SKIP - bad URL: {url}')
                    continue

                if self.is_already_scraped(subject_id):
                    continue

                print(f'[{i+1}/{len(movie_urls)}] Scraping subject {subject_id}...')

                try:
                    page.goto(url, timeout=30000)

                    page.wait_for_selector('div#info', timeout=15000)

                    html = page.content()
                    self.save_html(subject_id, html)
                    print(f'  -> Saved {len(html)} bytes')

                except Exception as e:
                    print(f'  -> ERROR: {type(e).__name__}: {e}')

                # Rate limiting: random delay between requests
                delay = random.uniform(3, 8)
                print(f'  -> Waiting {delay:.1f}s...')
                time.sleep(delay)

            browser.close()

        print('Scraping complete!')


if __name__ == '__main__':
    scraper = DoubanDetailScraper()
    scraper.scrape_all()
