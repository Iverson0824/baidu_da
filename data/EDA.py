import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

df = pd.read_parquet('data/douban_top250_cleaned.parquet')

print(f'dataset shape:{df.shape}')
print(f'Columns:{df.columns.tolist()}')

print('Descriptive stats:')
print(df[['rating','year','rating_count']].describe())

mean_rating = df['rating'].mean()
median_rating = df['rating'].median()
print(f'\nRating Mean:   {mean_rating:.2f}')
print(f'Rating Median: {median_rating:.2f}')
print(f'Difference:    {mean_rating - median_rating:.2f}')

df['decade'] = df['year'] // 10 * 10
print('Movies per decade:')
print(df['decade'].value_counts().sort_index())

# movie decade distribution plot
plt.figure(figsize=(12,6))
sns.countplot(data=df, x='decade')
plt.title('Douban Top 250: Movies by Decade')
plt.xlabel('Decade')
plt.ylabel('Number of Movies')
plt.tight_layout()
plt.savefig('data/decade_distribution.png', dpi=150)
plt.show()

# rating distribution kde
plt.figure(figsize=(12,6))
sns.histplot(data=df, x='rating', bins=13, kde=True)
plt.title('Douban Top 250: Rating Distribution with KDE')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('data/rating_kde.png', dpi=150)
plt.show()

# calculate skewness
skewness = df['rating'].skew()
print(f'\nRating Skewness: {skewness:.4f}')