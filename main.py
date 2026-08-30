from src.collector import get_fixtures

df = get_fixtures(league_id=39, season=2023)
print(df.head())