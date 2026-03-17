import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf



df = pd.read_csv('data/baidu_hotsearch_history.csv', parse_dates = ['date'])

daily_agg = df.groupby('date')['hot_index'].agg(
    daily_total = 'sum',
    daily_max = 'max',
    daily_avg = 'mean',
    daily_count = 'size'
)

print(f'Date range: {daily_agg.index.min()} to {daily_agg.index.max()}')
print(f'Days: {len(daily_agg)}')
print(daily_agg.describe())

daily_agg['rolling_mean'] = daily_agg['daily_total'].rolling(window = 7).mean()
daily_agg['rolling_std'] = daily_agg['daily_total'].rolling(window = 7).std()

# plot daily total and rolling mean
plt.figure(figsize=(14, 6))
plt.plot(daily_agg.index, daily_agg['daily_total'], label='Daily Total', alpha = 0.5)
plt.plot(daily_agg.index, daily_agg['rolling_mean'], label='Rolling Mean (7 days)', linewidth = 2, color = 'red')
plt.title('Baidu Hot Search Daily Total and Rolling Mean')
plt.xlabel('Date')
plt.ylabel('Daily Total Hot Index')
plt.legend()
plt.tight_layout()
plt.savefig('data/baidu_hotsearch_daily_total.png', dpi=150)
plt.show()

result = seasonal_decompose(daily_agg['daily_total'], model = 'additive', period = 7)

fig = result.plot()
fig.set_size_inches(14,10)
fig.tight_layout()
plt.savefig('data/baidu_hotsearch_trend.png', dpi=150)
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
plot_acf(daily_agg['daily_total'], lags=30, ax=ax1)
ax1.set_title('ACF - Autocorrelation')
plot_pacf(daily_agg['daily_total'], lags=30, ax=ax2)
ax2.set_title('PACF - Partial Autocorrelation')
fig.tight_layout()
fig.savefig('data/baidu_acf_pacf.png', dpi=150)
plt.show()

# topic lifecycle analysis
topic_lifecycle = df.groupby('title').agg(
    appearances=('date', 'count'),
    first_date=('date', 'min'),
    last_date=('date', 'max'),
    peak_hot_index=('hot_index', 'max'),
    peak_rank=('rank', 'min'),
    mean_hot_index=('hot_index', 'mean')
)
topic_lifecycle['tenure_days'] = (topic_lifecycle['last_date'] - topic_lifecycle['first_date']).dt.days + 1
topic_lifecycle = topic_lifecycle.sort_values('peak_hot_index', ascending=False)
print(f'\nUnique topics: {len(topic_lifecycle)}')
print(f'\nTop 30 hottest topics:')
print(topic_lifecycle.head(30).to_string())

plt.figure(figsize=(10, 6))
plt.hist(topic_lifecycle['tenure_days'], bins=range(1, topic_lifecycle['tenure_days'].max() + 2), 
         edgecolor='black', align='left')
plt.title('How Long Do Hot Topics Last?')
plt.xlabel('Tenure (days)')
plt.ylabel('Number of Topics')
plt.tight_layout()
plt.savefig('data/baidu_burst_pattern.png', dpi=150)
plt.show()

print(f'\nTenure distribution:')
print(topic_lifecycle['tenure_days'].value_counts().sort_index())

plt.figure(figsize=(10, 6))
plt.scatter(topic_lifecycle['peak_hot_index'], topic_lifecycle['tenure_days'], alpha=0.3)
plt.title('Peak Hot Index vs Topic Duration')
plt.xlabel('Peak Hot Index')
plt.ylabel('Tenure (days)')
plt.tight_layout()
plt.savefig('data/baidu_burst_scatter.png', dpi=150)
plt.show()

# day of week analysis
daily_agg['day_of_week'] = daily_agg.index.dayofweek
weekday_avg = daily_agg.groupby('day_of_week')['daily_total'].mean()
day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

plt.figure(figsize=(10, 6))
plt.bar(day_labels, weekday_avg.values, color='steelblue')
plt.title('Average Hot Search Volume by Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Mean Daily Total Hot Index')
plt.tight_layout()
plt.savefig('data/baidu_weekday_pattern.png', dpi=150)
plt.show()

print(f'\nWeekday averages:')
for day, avg in zip(day_labels, weekday_avg.values):
    print(f'  {day}: {avg:,.0f}')
