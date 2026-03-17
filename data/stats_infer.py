import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'STHeiti', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('data/douban_top250_cleaned.csv')
print(f"Total movies: {df.shape[0]}")
print(f"Total unique directors: {df['director'].nunique()}")

# Count films per director
director_counts = df['director'].value_counts()
print(f"\nDirector film counts:\n{director_counts.head()}")

# Filter: keep only directors with >= 3 films
qualified_directors = director_counts[director_counts >= 3].index
print(f"\nDirectors with >= 3 films: {len(qualified_directors)}")
print(f"Qualified directors: {qualified_directors.tolist()}")

df_anova = df[df['director'].isin(qualified_directors)].copy()
print(f"\nFiltered dataset: {df_anova.shape[0]} movies from {df_anova['director'].nunique()} directors")

print("Per-Director Summary Statistics")

director_stats = df_anova.groupby('director')['rating'].agg(
    ['count', 'mean', 'std', 'min', 'max']
).round(3)
director_stats.columns = ['n_films', 'mean_rating', 'std_rating', 'min_rating', 'max_rating']
director_stats = director_stats.sort_values('mean_rating', ascending=False)
print(director_stats.head().to_string())

# Box plot of ratings by director
plt.figure(figsize=(14, 7))
# sort directors by median rating
order = df_anova.groupby('director')['rating'].median().sort_values(ascending=False).index
sns.boxplot(data=df_anova, x='director', y='rating', order=order)
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.title('Douban Top 250: Rating Distribution by Director (≥3 films)', fontsize=14)
plt.xlabel('Director')
plt.ylabel('Rating')
plt.tight_layout()
plt.savefig('data/director_rating_boxplot.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nBox plot saved to data/director_rating_boxplot.png")

overall_mean = df_anova['rating'].mean()
print(f"Overall mean rating (filtered): {overall_mean:.3f}")
print(f"Highest group mean:  {director_stats['mean_rating'].max():.3f}")
print(f"Lowest group mean:   {director_stats['mean_rating'].min():.3f}")
print(f"Range of group means: {director_stats['mean_rating'].max() - director_stats['mean_rating'].min():.3f}")

# Shapiro-Wilk test for normality
print("\nShapiro-Wilk test for normality")

groups = [group['rating'].values for name, group in df_anova.groupby('director')]

all_normal = True
for name,group in df_anova.groupby('director'):
    stat, p = stats.shapiro(group['rating'])
    print(f"Group: {name}, {stat:.3f}, p={p:.3f}   {'Normal' if p > 0.05 else 'Not Normal'}")
    if p < 0.05:
        all_normal = False

if all_normal:
    print("All groups are normal")
else:
    print("Not all groups are normal")

# Levene's test for homogeneity of variances
print("\nLevene's test for homogeneity of variances")
stat, p = stats.levene(*groups)
print(f"Levene's test: F={stat:.3f}, p={p:.3f}   {'Homogeneous' if p > 0.05 else 'Not Homogeneous'}")

# ANOVA
print("\nOne-way ANOVA")
f_stat, anova_p = stats.f_oneway(*groups)
print(f"ANOVA: F={f_stat:.3f}, p={anova_p:.3f}   {'Significant' if anova_p < 0.05 else 'Not Significant'}")

# Kruskal-Wallis test
print("\nKruskal-Wallis test")
h_stat, kw_p = stats.kruskal(*groups)
print(f"Kruskal-Wallis test: H={h_stat:.3f}, p={kw_p:.3f}   {'Significant' if kw_p < 0.05 else 'Not Significant'}")

anova_sig = anova_p < 0.05
kw_sig = kw_p < 0.05

if anova_sig and kw_sig:
    print("\nBoth ANOVA and Kruskal-Wallis tests are significant")
elif anova_sig and not kw_sig:
    print("\nANOVA is significant, but Kruskal-Wallis test is not significant")
elif not anova_sig and kw_sig:
    print("\nANOVA is not significant, but Kruskal-Wallis test is significant")
else:
    print("\nNeither ANOVA nor Kruskal-Wallis test is significant")

# eta-squared
print("\nEta-squared")
all_mean = df_anova['rating'].mean()
ss_between =sum(len(g)*(g.mean()-all_mean)**2 for g in groups)
ss_total = sum((df_anova['rating']-all_mean)**2)
eta_squared = ss_between/ss_total
print(f"Eta-squared: {eta_squared:.3f}")



