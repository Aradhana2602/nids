from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import joblib
import pandas as pd

load_dotenv()
app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["nids_db"]

history_collection = db["scan_history"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and feature names
model = joblib.load("models/random_forest.pkl")
features = joblib.load("models/features.pkl")

# Original NSL-KDD column names
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

# Preprocessing function
def preprocess(df):

    # Assign column names
    df.columns = columns

    # Remove columns not used during training
    df = df.drop(
        ['label', 'difficulty'],
        axis=1
    )

    # One-hot encoding
    df = pd.get_dummies(
        df,
        columns=[
            'protocol_type',
            'service',
            'flag'
        ]
    )

    # Match training features
    df = df.reindex(
        columns=features,
        fill_value=0
    )

    return df


# Schema for single prediction
class TrafficData(BaseModel):
    data: list[float]


@app.get("/")
def home():
    return {
        "message": "NIDS API Running"
    }


@app.post("/predict")
def predict(payload: TrafficData):

    if len(payload.data) != len(features):
        return {
            "error": f"Expected {len(features)} features, got {len(payload.data)}"
        }

    sample = pd.DataFrame(
        [payload.data],
        columns=features
    )

    prediction = model.predict(sample)

    return {
        "prediction": int(prediction[0]),
        "result": "Attack" if prediction[0] == 1 else "Normal"
    }


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    # Read uploaded file
    df = pd.read_csv(
        file.file,
        header=None
    )

    # Preprocess data
    processed_df = preprocess(df)

    # Predict
    predictions = model.predict(
        processed_df
    )

    attacks = int((predictions == 1).sum())
    normal = int((predictions == 0).sum())

    total = len(predictions)

    attack_percentage = round(
        (attacks / total) * 100,
        2
    )

    if attack_percentage < 10:
        risk_level = "Low"
    elif attack_percentage < 40:
        risk_level = "Medium"
    else:
        risk_level = "High"

    history_collection.insert_one({
    "filename": file.filename,
    "total_records": total,
    "attacks": attacks,
    "normal": normal,
    "attack_percentage": attack_percentage,
    "risk_level": risk_level,
    "timestamp": datetime.now()
})
    
    return {
        "filename": file.filename,
        "total_records": total,
        "attacks": attacks,
        "normal": normal,
        "attack_percentage": attack_percentage,
        "risk_level": risk_level
    }

@app.get("/history")
def get_history():

    records = list(
        history_collection.find(
            {},
            {"_id": 0}
        )
        .sort("timestamp", -1)
        .limit(10)
    )

    return records