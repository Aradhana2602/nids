import pandas as pd
import joblib
import matplotlib.pyplot as plt

model = joblib.load("models/random_forest.pkl")

features = joblib.load(
    "models/features.pkl"
)

importance = model.feature_importances_

imp_df = pd.DataFrame({
    'Feature': features,
    'Importance': importance
})

imp_df = imp_df.sort_values(
    by='Importance',
    ascending=False
)

print(imp_df.head(20))

plt.figure(figsize=(12,8))

top_features = imp_df.head(15)

plt.barh(
    top_features['Feature'],
    top_features['Importance']
)

plt.xlabel("Importance")
plt.ylabel("Features")
plt.title("Top 15 Important Features")

plt.tight_layout()
plt.show()