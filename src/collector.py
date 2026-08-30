import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {
    "X-RapidAPI-Key": os.getenv("API_KEY"),
}

def _get(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data["response"]


def get_fixtures(league_id, season, status="FT"):
    results = _get("fixtures", {
        "league": league_id,
        "season": season,
        "status": status
    })
    
    matches = []
    for fixture in results:
        matches.append({
            "fixture_id":    fixture["fixture"]["id"],
            "date":          fixture["fixture"]["date"],
            "home_team_id":  fixture["teams"]["home"]["id"],
            "home_team":     fixture["teams"]["home"]["name"],
            "away_team_id":  fixture["teams"]["away"]["id"],
            "away_team":     fixture["teams"]["away"]["name"],
            "home_goals":    fixture["goals"]["home"],
            "away_goals":    fixture["goals"]["away"],
            "status":        fixture["fixture"]["status"]["short"]
        })
    
    df = pd.DataFrame(matches)
    df.to_csv(f"data/raw/fixtures_{league_id}_{season}.csv", index=False)
    print(f"{len(matches)} matchs sauvegardés.")
    return df


def get_team_stats(team_id, league_id, season):
    result = _get("teams/statistics", {
        "team":   team_id,
        "league": league_id,
        "season": season
    })
    
    stats = {
        "team_id":          team_id,
        "wins":             result["fixtures"]["wins"]["total"],
        "draws":            result["fixtures"]["draws"]["total"],
        "losses":           result["fixtures"]["loses"]["total"],
        "goals_scored":     result["goals"]["for"]["total"]["total"],
        "goals_conceded":   result["goals"]["against"]["total"]["total"],
        "form":             result["form"]
    }
    
    return stats


def get_head_to_head(team1_id, team2_id):
    results = _get("fixtures/headtohead", {
        "h2h":  f"{team1_id}-{team2_id}",
        "last": 10
    })
    
    h2h = []
    for fixture in results:
        h2h.append({
            "date":         fixture["fixture"]["date"],
            "home_team_id": fixture["teams"]["home"]["id"],
            "away_team_id": fixture["teams"]["away"]["id"],
            "home_goals":   fixture["goals"]["home"],
            "away_goals":   fixture["goals"]["away"]
        })
    
    return h2h