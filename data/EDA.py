import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'STHeiti', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

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

# Decade region cross analysis
print(f'\n{df['countries'].str.split(', ').explode().value_counts()}')

df_exploded = df.assign(country=df['countries'].str.split(', ')).explode('country').reset_index(drop=True)
region_map = {
    # for countires with more than 2 movies in the dataset
    '美国':'North America',
    '英国':'Europe',
    '日本':'Asia',
    '法国':'Europe',
    '德国':'Europe',
    '意大利':'Europe',
    '加拿大':'North America',
    '澳大利亚':'Oceania',
    '印度':'Asia',
    '新西兰':'Oceania',
    '西班牙':'Europe',
    '韩国':'Asia',
    '中国香港':'Asia',
    '中国大陆':'Asia',
    '中国台湾':'Asia',
    '瑞士':'Europe'
}
df_exploded['region'] = df_exploded['country'].map(region_map).fillna('Other')
print(f'\n{df_exploded['region'].value_counts()}')

crosstab = pd.crosstab(df_exploded['decade'], df_exploded['region'])
print(f'\n{crosstab}')

# Chi-square test
chi2, p, dof, expected = stats.chi2_contingency(crosstab)
print(f'\nChi-square test: chi2= {chi2:.3f}')
print(f'p= {p:.3f}')
print(f'dof= {dof}')
print(pd.DataFrame(expected, index=crosstab.index, columns=crosstab.columns).round(1))

plt.figure(figsize=(12,8))
sns.heatmap(crosstab, annot=True, fmt='d', cmap='YlOrRd')
plt.title('Movie Count by Region and Decade')
plt.xlabel('Region')
plt.ylabel('Decade')
plt.tight_layout()
plt.savefig('data/movie_count_region_decade.png', dpi=150)
plt.show()

plt.figure(figsize=(14, 7))
sns.boxplot(data=df_exploded, x='decade', y='rating', hue='region')
plt.title('Rating Distribution by Decade and Region')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/decade_region_boxplot.png', dpi=150)
plt.show()

# Genre analysis
print(f'\nGenre analysis')
genre_dummies = df['genres'].str.get_dummies(sep=', ')
print(f'{genre_dummies.sum().sort_values(ascending=False)}')

# Point-biserial correlation
genre_corr = []
for genre in genre_dummies.columns:
    genre_corr.append(stats.pointbiserialr(genre_dummies[genre], df['rating']))
genre_corr_df = pd.DataFrame(genre_corr, columns=['correlation', 'p-value'], index=genre_dummies.columns).sort_values(by='correlation', ascending=False)
print(genre_corr_df)

# Mean rating by genre
genre_stats = []
for genre in genre_dummies.columns:
    ratings = df[genre_dummies[genre] == 1]["rating"]
    genre_stats.append({
        'genre': genre,
        'mean': ratings.mean(),
        'ci': 1.96 * ratings.std() / (len(ratings) ** 0.5) if len(ratings) > 1 else 0,
        'count': len(ratings)
    })

genre_stats_df = pd.DataFrame(genre_stats).sort_values(by='mean', ascending=False)

plt.figure(figsize=(10, 8))
plt.barh(genre_stats_df['genre'], genre_stats_df['mean'], xerr=genre_stats_df['ci'], color='steelblue')
plt.xlim(8.4, 9.6)
plt.tight_layout()
plt.xlabel('Mean Rating')
plt.title('Mean Rating by Genre (with 95% CI)')
plt.tight_layout()
plt.savefig('data/genre_rating_analysis.png', dpi=150)
plt.show()

# Genre co-occurrence
cooccurrence = genre_dummies.T.dot(genre_dummies)

plt.figure(figsize=(14, 12))
sns.heatmap(cooccurrence, annot=True, fmt='d', cmap='YlOrRd')
plt.title('Genre Co-occurrence Matrix')
plt.tight_layout()
plt.savefig('data/genre_cooccurrence.png', dpi=150)
plt.show()

# Director and Actor analysis
df_actors = df.assign(actor =df['cast_members'].str.split(', ')).explode('actor').reset_index(drop=True)
actor_stats = df_actors.groupby('actor')['rating'].agg(['count', 'mean']).sort_values(by='count', ascending=False)
filtered_actors = actor_stats[actor_stats['count'] >= 2]
print(f'\nActors with >= 2 movies: {filtered_actors.shape[0]}')
print(filtered_actors.head(20).to_string())

# Spearman correlation between actor count and mean rating
rho, p = stats.spearmanr(filtered_actors['count'], filtered_actors['mean'])
if rho > 0 and p<0.05:
    print(f'\nSpearman correlation: rho={rho:.3f}, p={p:.3f} (Positive correlation between actor count and mean rating)')
elif rho < 0 and p<0.05:
    print(f'\nSpearman correlation: rho={rho:.3f}, p={p:.3f} (Negative correlation between actor count and mean rating)')
else:
    print(f'\nSpearman correlation: rho={rho:.3f}, p={p:.3f} (No significant correlation between actor count and mean rating)')

# director productivity vs quality(rating)
dir_stats = df.groupby('director')['rating'].agg(['count','mean']).sort_values(by='count', ascending=False)
filtered_dir = dir_stats[dir_stats['count'] >= 2]

plt.figure(figsize = (12,6))
plt.scatter(filtered_dir['count'], filtered_dir['mean'])
z = np.polyfit(filtered_dir['count'], filtered_dir['mean'], 1)
p = np.poly1d(z)
x_line = np.linspace(filtered_dir['count'].min(), filtered_dir['count'].max(), 100)
plt.plot(x_line, p(x_line), 'r--')
plt.title('Director Productivity vs Quality')
plt.xlabel('Number of Movies')
plt.ylabel('Mean Rating')
plt.tight_layout()
plt.savefig('data/director_productivity_quality.png', dpi=150)
plt.show()

print(f'Regression slope: {z[0]:.4f}')
