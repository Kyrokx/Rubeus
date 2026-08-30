import pandas as pd
from src.collector import get_team_stats, get_head_to_head


def compute_form(form_string, last_n=5) -> int:
    """
    Transforme "WWLWD" en score de forme entre 0 et 1.
    W = 3 points, D = 1 point, L = 0 point
    Max possible sur 5 matchs = 15 points
    """
    form = form_string[-last_n:]  # on prend les N derniers
    points = 0
    for result in form:
        if result == "W":
            points += 3
        elif result == "D":
            points += 1
    return round(points / (last_n * 3), 2)  # normalise entre 0 et 1


def compute_h2h_score(h2h, team_id) -> int:
    """
    Sur les confrontations directes, quel % de matchs cette équipe a gagné ?
    """
    if not h2h:
        return 0.5  # pas d'historique → on suppose 50/50

    wins = 0
    for match in h2h:
        home = match["home_team_id"]
        away = match["away_team_id"]
        hg   = match["home_goals"]
        ag   = match["away_goals"]

        if home == team_id and hg > ag:
            wins += 1
        elif away == team_id and ag > hg:
            wins += 1

    return round(wins / len(h2h), 2)


def build_match_features(home_id, away_id, league_id, season) -> dict:
    """
    Construit toutes les features d'un match donné.
    Retourne un dictionnaire prêt à rentrer dans le modèle.
    """
    home_stats = get_team_stats(home_id, league_id, season)
    away_stats = get_team_stats(away_id, league_id, season)
    # h2h        = get_head_to_head(home_id, away_id)

    total_home = home_stats["wins"] + home_stats["draws"] + home_stats["losses"]
    total_away = away_stats["wins"] + away_stats["draws"] + away_stats["losses"]

    features = {
        # Forme récente
        "home_form": compute_form(home_stats["form"]),
        "away_form": compute_form(away_stats["form"]),

        # Taux de victoire sur la saison
        "home_win_rate":  round(home_stats["wins"]  / total_home, 2),
        "away_win_rate":  round(away_stats["wins"]  / total_away, 2),

        # Moyenne de buts
        "home_goals_scored_avg":   round(home_stats["goals_scored"]   / total_home, 2),
        "home_goals_conceded_avg": round(home_stats["goals_conceded"] / total_home, 2),
        "away_goals_scored_avg":   round(away_stats["goals_scored"]   / total_away, 2),
        "away_goals_conceded_avg": round(away_stats["goals_conceded"] / total_away, 2),

        # Head to head
        #"h2h_home": compute_h2h_score(h2h, home_id),
        #"h2h_away": compute_h2h_score(h2h, away_id),
    }

    return features


def build_training_data(fixtures_df, league_id, season) -> pd.DataFrame:
    """
    Parcourt tous les matchs terminés et construit le dataset d'entraînement.
    Ajoute la colonne 'result' : 1 = domicile gagne, 0 = nul, 2 = extérieur gagne
    """
    rows = []

    for _, row in fixtures_df.iterrows():
        try:
            features = build_match_features(
                home_id=row["home_team_id"],
                away_id=row["away_team_id"],
                league_id=league_id,
                season=season
            )

            # Calcul du résultat réel
            if row["home_goals"] > row["away_goals"]:
                result = 1   # victoire domicile
            elif row["home_goals"] == row["away_goals"]:
                result = 0   # nul
            else:
                result = 2   # victoire extérieur

            features["result"] = result
            rows.append(features)

        except Exception as e:
            print(f"Erreur sur le match {row['fixture_id']} : {e}")
            continue

    df = pd.DataFrame(rows)
    df.to_csv("data/processed/training_data.csv", index=False)
    print(f"Dataset prêt : {len(df)} matchs.")
    return df