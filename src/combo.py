from src.model import predict

SEUIL_SAFE   = 0.60  # combiné prudent
SEUIL_RISQUE = 0.50  # combiné risqué

def build_combo(matches: list) -> dict:
    """
    matches = liste de dicts :
    [
        {
            "home": "Arsenal",
            "away": "Chelsea",
            "features": { ... },
            "cote_home": 1.85,
            "cote_nul":  3.40,
            "cote_away": 4.20
        },
        ...
    ]
    """
    resultats = []

    for match in matches:
        probas = predict(match["features"])

        # Trouve le résultat le plus probable (hors nul)
        if probas["domicile"] >= probas["exterieur"]:
            meilleur       = "domicile"
            proba_max      = probas["domicile"]
            cote           = match["cote_home"]
            label          = f"{match['home']} gagne"
        else:
            meilleur       = "exterieur"
            proba_max      = probas["exterieur"]
            cote           = match["cote_away"]
            label          = f"{match['away']} gagne"

        resultats.append({
            "match":     f"{match['home']} vs {match['away']}",
            "prediction": label,
            "proba":      proba_max,
            "cote":       cote,
            "probas":     probas
        })

    # Trie par confiance décroissante
    resultats.sort(key=lambda x: x["proba"], reverse=True)

    # Filtre selon les seuils
    combo_safe   = [r for r in resultats if r["proba"] >= SEUIL_SAFE]
    combo_risque = [r for r in resultats if r["proba"] >= SEUIL_RISQUE]

    def calcule_combo(selection):
        if not selection:
            return None
        cote_combined = 1.0
        proba_combined = 1.0
        for r in selection:
            cote_combined  *= r["cote"]
            proba_combined *= r["proba"]
        return {
            "selections":      selection,
            "cote_combinee":   round(cote_combined, 2),
            "proba_combinee":  round(proba_combined, 3),
            "esperance":       round(proba_combined * cote_combined, 3)
        }

    return {
        "tous":         resultats,
        "combo_safe":   calcule_combo(combo_safe),
        "combo_risque": calcule_combo(combo_risque)
    }


def affiche_combo(resultat: dict):
    print("\n" + "="*50)
    print("🔴 RUBEUS — Analyse des matchs")
    print("="*50)

    print("\n📊 Toutes les prédictions :")
    for r in resultat["tous"]:
        print(f"  {r['match']}")
        print(f"    → {r['prediction']} ({r['proba']:.0%} confiance, cote {r['cote']})")
        print(f"    → Probas : Dom {r['probas']['domicile']:.0%} | Nul {r['probas']['nul']:.0%} | Ext {r['probas']['exterieur']:.0%}")

    for nom, combo in [("✅ SAFE", resultat["combo_safe"]), ("⚡ RISQUÉ", resultat["combo_risque"])]:
        print(f"\n{nom} :")
        if not combo:
            print("  Aucun match assez confiant.")
        else:
            for r in combo["selections"]:
                print(f"  ✓ {r['prediction']} ({r['proba']:.0%})")
            print(f"  Cote combinée  : {combo['cote_combinee']}")
            print(f"  Proba combinée : {combo['proba_combinee']:.1%}")
            print(f"  Espérance      : {combo['esperance']} (>1 = rentable)")