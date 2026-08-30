import pandas as pd
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_PATH = "models/rubeus_v1.pkl"

def train(data_path="data/processed/training_data.csv"):
    df = pd.read_csv(data_path)

    X = df.drop(columns=["result"])
    y = df["result"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    eval_metric="mlogloss",
    random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Précision : {acc:.2%}")
    print(classification_report(y_test, y_pred, target_names=["Nul", "Dom.", "Ext."]))

    joblib.dump(model, MODEL_PATH)
    print(f"Modèle sauvegardé → {MODEL_PATH}")

    return model


def predict(features: dict):
    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([features])
    probas = model.predict_proba(df)[0]

    return {
        "nul":      round(probas[0], 3),
        "domicile": round(probas[1], 3),
        "exterieur": round(probas[2], 3)
    }