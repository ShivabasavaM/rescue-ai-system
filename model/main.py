from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import torch
from torchvision import models, transforms
import torch.nn as nn
import io
from PIL import Image
import os

CRITICAL_THRESHOLD = float(os.getenv("CRITICAL_THRESHOLD","0.40"))
DB_PATH = os.getenv("DB_PATH","dispatch.db")
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH","production_mobilenet_weights.pth")
ROLLING_LIMIT = int(os.getenv("ROLLING_LIMIT","15"))
ALLOWED_CONTENT_IMAGES = {"image/jpeg","image/png"}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            create table if not exists incidents(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                priority TEXT NOT NULL,
                confidence TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending_dispatch',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def log_incident(priority : str, confidence : str) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        c.execute(
            "INSERT INTO incidents (priority, confidence, status) values (?,?,?)",
            (priority, confidence, 'pending_dispatch')
        )
        row_id = c.lastrowid
        incident_id =f"REP-{row_id:03d}"

        c.execute(
            "UPDATE incidents SET incident_id = ? where id=?",
            (incident_id, row_id)
        )
        
        c.execute(
            """
            DELETE from incidents 
            where id not in (
            SELECT id 
            from Incidents
            order by id DESC LIMIT ?
            )
        """,
        (ROLLING_LIMIT,))
        conn.commit()

    print(f"[DB] Incident id : {incident_id} | logged | Priority : {priority} | Confidence : {confidence}")
    return incident_id

def get_all_incidents() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM Incidents order by id DESC").fetchall()
    return [dict(row) for row in rows]


device = torch.device("cpu")
class_names = ["Safe","Critical"]


def build_model() -> nn.Module:
    m = models.mobilenet_v3_small(weights=None)
    num_ftrs = m.classifier[3].in_features
    m.classifier[3] = nn.Linear(num_ftrs, len(class_names))

    if not os.path.exists(WEIGHTS_PATH):
        raise RuntimeError(f"Model weights not found at '{WEIGHTS_PATH}'. ")

    m.load_state_dict(torch.load(WEIGHTS_PATH,map_location=device))
    m.eval()
    print(f"[Model] Weights loaded from '{WEIGHTS_PATH}")
    return m


inference_transforms = transforms.Compose([
    transforms.Resize((256,256)),
    transforms.CenterCrop((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

model : nn.Module | None = None 

@asynccontextmanager
async def lifespan (app : FastAPI):
    global model
    init_db()
    print("[DB] Database initialised.")
    model = build_model()
    yield

app = FastAPI(
    title= "Rescue AI Triage API",
    description = "Accepts dog images, runs MobilenetV3 triage log incidents to the SQlite. ",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["POST","GET"],
    allow_headers=["*"]
)

def run_inference(image : Image.Image) -> tuple[str, float]:
    input_tensor = inference_transforms(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

    safe_prob = probabilities[0].item()
    critical_prob = probabilities[1].item()

    if critical_prob >= CRITICAL_THRESHOLD:
        return "critical", critical_prob
    return "safe", safe_prob 

#APP routage code:

@app.get("/health")
def health_check():
    return {"status":"ok", "model loaded": model is not None }

@app.get("/api/incidents")
def list_all_incidents():
    return {"incidents": get_all_incidents()}

@app.post("/api/triage")
async def triage_incident(file : UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_IMAGES:
        raise HTTPException(
            status_code = 400,
            detail = (
                f"Unsupported file type '{file.content_type}. "
                "Only JPEG and PNG are accepted"
            ),
        )
    
    image_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code = 400,
            detail = "Could not decode the Uploaded file as an image.",
        )

    priority, display_confidence = run_inference(image)
    confidence_str = f"{display_confidence* 100:.1f}%"

    incident_id  = log_incident(priority, confidence_str)

    return {
        "message" : "Triage Complete.",
        "incident_id": incident_id,
        "priority" : priority,
        "confidence" : confidence_str,
        "display_status" :"Logged to DB"
    }

@app.patch("/api/incidents/{incident_id}/dispatch")
def mark_incident_dispatched(incident_id: str):
    """Updates the status of an incident to 'dispatched'."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE incidents SET status = 'dispatched' WHERE incident_id = ?",
            (incident_id,)
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        conn.commit()
        
    return {"message": f"Incident {incident_id} marked as dispatched."}