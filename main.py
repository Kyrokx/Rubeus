from src.features import build_match_features
from src.combo import build_combo, affiche_combo

# Exemples de matchs à venir avec leurs cotes
matches = [
    {
        "home": "Arsenal",
        "away": "Chelsea",
        "features": build_match_features(42, 49, 39, 2024),
        "cote_home": 1.85,
        "cote_nul":  3.40,
        "cote_away": 4.20
    },
    {
        "home": "Liverpool",
        "away": "Manchester City",
        "features": build_match_features(40, 50, 39, 2024),
        "cote_home": 2.10,
        "cote_nul":  3.50,
        "cote_away": 3.20
    },
    {
        "home": "Manchester United",
        "away": "Tottenham",
        "features": build_match_features(33, 47, 39, 2024),
        "cote_home": 2.40,
        "cote_nul":  3.20,
        "cote_away": 2.90
    }
]

resultat = build_combo(matches)
affiche_combo(resultat)