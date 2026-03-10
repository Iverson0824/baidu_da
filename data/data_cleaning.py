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

# save cleaned dataset
df.to_parquet('data/douban_top250_cleaned.parquet')
df.to_csv('data/douban_top250_cleaned.csv', index=False)
print('cleaned dataset saved')
