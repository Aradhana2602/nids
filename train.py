import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)
import joblib

columns = [
'duration',
'protocol_type',
'service',
'flag',
'src_bytes',
'dst_bytes',
'land',
'wrong_fragment',
'urgent',
'hot',
'num_failed_logins',
'logged_in',
'num_compromised',
'root_shell',
'su_attempted',
'num_root',
'num_file_creations',
'num_shells',
'num_access_files',
'num_outbound_cmds',
'is_host_login',
'is_guest_login',
'count',
'srv_count',
'serror_rate',
'srv_serror_rate',
'rerror_rate',
'srv_rerror_rate',
'same_srv_rate',
'diff_srv_rate',
'srv_diff_host_rate',
'dst_host_count',
'dst_host_srv_count',
'dst_host_same_srv_rate',
'dst_host_diff_srv_rate',
'dst_host_same_src_port_rate',
'dst_host_srv_diff_host_rate',
'dst_host_serror_rate',
'dst_host_srv_serror_rate',
'dst_host_rerror_rate',
'dst_host_srv_rerror_rate',
'label',
'difficulty'
]

df = pd.read_csv(
    "data/KDDTrain+.txt",
    names=columns
)

# print("Dataset Shape:", df.shape)

# print("\nFirst 5 rows:")
# print(df.head())

# print("\nUnique Labels:")
# print(df['label'].value_counts().head(20))

# Convert to binary classification
df['label'] = df['label'].apply(
    lambda x: 0 if x == 'normal' else 1
)

print(df['label'].value_counts())

df = pd.get_dummies(
    df,
    columns=[
        'protocol_type',
        'service',
        'flag'
    ]
)

print(df.shape)

X = df.drop(
    ['label', 'difficulty'],
    axis=1
)

y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print(X_train.shape)
print(X_test.shape)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("Training Complete")

preds = model.predict(X_test)

print(
    "Accuracy:",
    accuracy_score(
        y_test,
        preds
    )
)

print(
    confusion_matrix(
        y_test,
        preds
    )
)

print(
    classification_report(
        y_test,
        preds
    )
)

joblib.dump(
    model,
    "models/random_forest.pkl"
)
joblib.dump(
    X.columns.tolist(),
    "models/features.pkl"
)

print("Model Saved")

# import pandas as pd
# import joblib
# import matplotlib.pyplot as plt

# model = joblib.load("models/random_forest.pkl")

# importance = model.feature_importances_

# features = X.columns

# imp_df = pd.DataFrame({
#     'Feature': features,
#     'Importance': importance
# })

# imp_df = imp_df.sort_values(
#     by='Importance',
#     ascending=False
# )

# print(imp_df.head(20))