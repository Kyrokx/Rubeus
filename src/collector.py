import requests
import os
import pandas as pd
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = "https://v3.football.api-sports.io"
DATA_RAW_PATH = 'data/raw'

HEADERS = {
    "x-apisports-key": os.getenv("API_KEY")
}

def _get(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data["response"]


def get_fixtures(league_id, season, status="FT") -> pd.DataFrame:
    results = _get("fixtures", {
        "league": league_id,
        "season": season,
        "status": status
    })

    matches = []
    for fixture in results:
        matches.append({
            "fixture_id":   fixture["fixture"]["id"],
            "date":         fixture["fixture"]["date"],
            "home_team_id": fixture["teams"]["home"]["id"],
            "home_team":    fixture["teams"]["home"]["name"],
            "away_team_id": fixture["teams"]["away"]["id"],
            "away_team":    fixture["teams"]["away"]["name"],
            "home_goals":   fixture["goals"]["home"],
            "away_goals":   fixture["goals"]["away"],
            "status":       fixture["fixture"]["status"]["short"]
        })

    df = pd.DataFrame(matches)
    df.to_csv(f"{DATA_RAW_PATH}/fixtures_{league_id}_{season}.csv", index=False)
    print(f"{len(matches)} matchs sauvegardés.")
    return df


def get_team_stats(team_id, league_id, season) -> dict:
    cache_path = f"{DATA_RAW_PATH}/stats_{team_id}_{league_id}_{season}.json"

    # Relit depuis le cache si disponible
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    result = _get("teams/statistics", {
        "team":   team_id,
        "league": league_id,
        "season": season
    })

    if not result:
        return None

    stats = {
        "team_id":        int(team_id),
        "wins":           result["fixtures"]["wins"]["total"],
        "draws":          result["fixtures"]["draws"]["total"],
        "losses":         result["fixtures"]["loses"]["total"],
        "goals_scored":   result["goals"]["for"]["total"]["total"],
        "goals_conceded": result["goals"]["against"]["total"]["total"],
        "form":           result["form"]
    }

    # Sauvegarde seulement si données valides
    with open(cache_path, "w") as f:
        json.dump(stats, f)

    return stats


def get_head_to_head(team1_id, team2_id) -> list:
    cache_path = f"{DATA_RAW_PATH}/h2h_{team1_id}_{team2_id}.json"

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

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

    with open(cache_path, "w") as f:
        json.dump(h2h, f)

    return h2h