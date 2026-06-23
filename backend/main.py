from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from fastapi.responses import FileResponse
import os
import joblib
import pandas as pd
# import shap

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
# explainer = shap.TreeExplainer(model)
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

# Schema for PDF report generation
class ReportData(BaseModel):
    filename: str
    total_records: int
    attacks: int
    normal: int
    attack_percentage: float
    risk_level: str


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

    # attack_indices = processed_df[predictions == 1].index

    # if len(attack_indices) > 0:

    #     sample = processed_df.iloc[[attack_indices[0]]]

    #     shap_values = explainer.shap_values(sample)

    #     print("SHAP GENERATED")
    #     print(type(shap_values))

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

@app.post("/generate-report")
def generate_report(data: ReportData):

    pdf_file = "nids_report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "AI-Powered NIDS Report")

    c.setFont("Helvetica", 12)

    c.drawString(100, 760, f"Filename: {data.filename}")
    c.drawString(100, 730, f"Total Records: {data.total_records}")
    c.drawString(100, 700, f"Attacks: {data.attacks}")
    c.drawString(100, 670, f"Normal: {data.normal}")
    c.drawString(
        100,
        640,
        f"Attack Percentage: {data.attack_percentage}%"
    )
    c.drawString(
        100,
        610,
        f"Risk Level: {data.risk_level}"
    )

    c.save()

    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="nids_report.pdf"
    )