import os
import re
from bs4 import BeautifulSoup
from utils.mysql_helper import MysqlHelper

class DoubanParser:
    def __init__(self, data_dir='data/db_top250_raw'):
        self.data_dir = data_dir

    def load_html(self, page):
        filepath = os.path.join(self.data_dir, f'page_{page}.html')
        with open(filepath, 'r', encoding = 'utf-8') as f:
            return f.read()
    
    def parse_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        movies = []
        items = soup.select('ol.grid_view > li')
        
        for item in items:
            movie = {}
            movie['rank'] = int(item.select_one('div.pic > em').get_text(strip=True))
            movie['title'] = item.select_one('span.title').get_text(strip=True)
            movie['rating'] = float(item.select_one('span.rating_num').get_text(strip=True))
            count_span = item.find('span', string=re.compile(r'人评价'))
            if count_span:
                movie['rating_count'] = int(re.search(r'\d+', count_span.get_text()).group())
            movie['quote'] = item.select_one('p.quote').get_text(strip=True) if item.select_one('p.quote') else None
            movie['link'] = item.select_one('div.pic > a')['href']
            movie['movie_info'] = item.select_one('div.bd p').get_text(strip=True)
            movie.update(self.clean_movie_info(movie['movie_info']))
            movies.append(movie)
        return movies

    def clean_movie_info(self, movie_info):
        movie_info = movie_info.replace('\xa0', ' ')
        director_match = re.search(r'导演:\s*(.*?)(?:\s*主演|\.\.\.)', movie_info)
        year_match = re.search(r'(\d{4})',movie_info)
        parts = movie_info.split('/')
        country = parts[-2].strip() if len(parts) >= 3 else None
        genre = parts[-1].strip() if len(parts) >= 3 else None
        return {
            'director': director_match.group(1).strip() if director_match else None,
            'year': year_match.group(1) if year_match else None,
            'country': country,
            'genre': genre
        }
        
        
    
    def parse_all(self):
        all_movies = []
        for page in range(10):
            filepath = os.path.join(self.data_dir, f'page_{page}.html')
            if os.path.exists(filepath) and os.path.getsize(filepath) > 50000:
                html = self.load_html(page)
                movies = self.parse_page(html)
                all_movies.extend(movies)
                print(f'Parsed page {page+1}: {len(movies)} movies')
        print(f'Total parsed movies: {len(all_movies)}')
        return all_movies

    def to_db(self, movies):
        mysql_helper = MysqlHelper()
        query = """
            INSERT IGNORE INTO douban_top250 (
                rank_idx,
                title,
                rating,
                rating_count,
                quote,
                link,
                director,
                year
            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        """

        genre_query = """
            INSERT IGNORE INTO movie_genres (movie_id, genre) VALUES(%s, %s)
        """

        country_query = """
            INSERT IGNORE INTO movie_countries (movie_id, country) VALUES(%s, %s)
        """

        with mysql_helper.transaction() as cursor:
            for movie in movies:
                cursor.execute(query, (
                    movie['rank'],
                    movie['title'],
                    movie['rating'],
                    movie['rating_count'],
                    movie['quote'],
                    movie['link'],
                    movie['director'],
                    movie['year']
                ))
            
                cursor.execute('SELECT LAST_INSERT_ID() AS id')
                movie_id = cursor.fetchone()[0]

                if movie_id == 0:
                    cursor.execute('SELECT id FROM douban_top250 WHERE rank_idx = %s', (movie['rank'],))
                    movie_id = cursor.fetchone()[0]
            
                if movie.get('genre'):
                    for genre in movie['genre'].strip().split(' '):
                        cursor.execute(genre_query, (movie_id, genre))
            
                if movie.get('country'):
                    for country in movie['country'].strip().split(' '):
                        cursor.execute(country_query, (movie_id, country))
        print(f'Successfully inserted {len(movies)} movies into the database.')
    
if __name__ == '__main__':
    parser = DoubanParser()
    movies = parser.parse_all()
    parser.to_db(movies)

    for m in movies[:3]:
        print(m)
