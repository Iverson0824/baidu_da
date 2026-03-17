import json
import pandas as pd
from pathlib import Path

raw_dir = Path('data/baidu_hot_search_raw/raw')
all_entries = []
for json_file in sorted (raw_dir.glob('*.json')):
    date = pd.to_datetime(json_file.stem, format='%Y%m%d')
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for rank, (title, info) in enumerate(data.items(), 1):
        all_entries.append({
            'date':date,
            'rank':rank,
            'title':title,
            'hot_index': info['hot'],
            'url':info['href']
        })

df = pd.DataFrame(all_entries)
df = df.sort_values(['date', 'rank']).reset_index(drop=True)

print(f'Total entries: {len(df)}')
print(f'Date range: {df["date"].min()} to {df["date"].max()}')
print(f'Entries per day:\n{df.groupby("date").size().describe()}')
df.to_csv('data/baidu_hotsearch_history.csv', index=False)