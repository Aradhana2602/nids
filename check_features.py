import joblib

features = joblib.load(
    "models/features.pkl"
)

print("Number of Features:", len(features))