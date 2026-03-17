import pandas as pd
from sqlalchemy import create_engine

# build connection engine
engine = create_engine('mysql+pymysql://baidu_da:1!Asdfghjkl@localhost:3306/practice_db')

# read data from table
query = "SELECT * FROM douban_top250"
df = pd.read_sql(query, engine)

print(f'shape: {df.shape}')
print(df.head())

print('column names:')
print(df.columns.tolist())

print('info:')
print(df.info())

print('descriptive stats:')
print(df.describe())

print('missing values:')
print(df.isnull().sum())

# enable pyarrow
# convert to pyarrow dtype
print('before pyarrow')
print(df.dtypes)

df = df.convert_dtypes(dtype_backend='pyarrow')

print('after pyarrow')
print(df.dtypes)

# cleaning
# remove whitespace
string_cols = df.select_dtypes(include='string').columns
for col in string_cols:
    df[col] = df[col].str.strip()

# check year 
df['year'] = pd.to_numeric(df['year'], errors='coerce')
print(f'year range: {df['year'].min()} - {df['year'].max()}')
print(f'Missing years: {df['year'].isnull().sum()}')

# deduplication
duplicates = df[df.duplicated(subset=['rank_idx'], keep=False)]
print(f'Duplciated rows: {len(duplicates)}')

# memory optimization
print(f'memory before: {df.memory_usage(deep=True).sum()/1024:.1f}KB')
df['year'] = pd.to_numeric(df['year'], downcast='integer')
df['rating_count'] = pd.to_numeric(df['rating_count'], downcast='integer')
print(f'Memory after:  {df.memory_usage(deep=True).sum() / 1024:.1f} KB')

# outlier
mean = df['rating'].mean()
std = df['rating'].std()
lower = mean - 3 * std
upper = mean + 3 * std
outliers = df[(df['rating'] < lower) | (df['rating'] > upper)]
print(f'\n3σ range: [{lower:.2f}, {upper:.2f}]')
print(f'Outliers: {len(outliers)}')
if len(outliers) > 0:
    print(outliers[['rank_idx', 'title', 'rating']])

# join cast data from movie_cast junction table
cast_query = """
    SELECT d.rank_idx, GROUP_CONCAT(mc.actor_name ORDER BY mc.id SEPARATOR ', ') AS cast_members
    FROM movie_cast mc
    JOIN douban_top250 d ON mc.movie_id = d.id
    GROUP BY d.rank_idx
"""
cast_df = pd.read_sql(cast_query, engine)
cast_df = cast_df.convert_dtypes(dtype_backend='pyarrow')
df = df.merge(cast_df, on='rank_idx', how='left')
print(f'Cast data merged: {df["cast_members"].notna().sum()} movies have cast info')

# join genre data from movie_genres junction table
genre_query = """
    SELECT d.rank_idx, GROUP_CONCAT(mg.genre ORDER BY mg.id SEPARATOR ', ') AS genres
    FROM movie_genres mg
    JOIN douban_top250 d ON mg.movie_id = d.id
    GROUP BY d.rank_idx
"""
genre_df = pd.read_sql(genre_query, engine)
genre_df = genre_df.convert_dtypes(dtype_backend='pyarrow')
df = df.merge(genre_df, on='rank_idx', how='left')

# join country data from movie_countries junction table
country_query = """
    SELECT d.rank_idx, GROUP_CONCAT(mc.country ORDER BY mc.id SEPARATOR ', ') AS countries
    FROM movie_countries mc
    JOIN douban_top250 d ON mc.movie_id = d.id
    GROUP BY d.rank_idx
"""
country_df = pd.read_sql(country_query, engine)
country_df = country_df.convert_dtypes(dtype_backend='pyarrow')
df = df.merge(country_df, on='rank_idx', how='left')

print(f'Final columns: {df.columns.tolist()}')

# save cleaned dataset
df.to_parquet('data/douban_top250_cleaned.parquet')
df.to_csv('data/douban_top250_cleaned.csv', index=False)
print('cleaned dataset saved')
