from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import uuid
import httpx
import json
import os
from filelock import FileLock

app = FastAPI(title="Rescue AI Triage & Webhook Hub")

device = torch.device("cpu") 

class_names = ['Safe', 'Critical'] # Index 0 = healthy (Safe), Index 1 = unhealthy (Critical)

# Build the MobileNetV3 shell
model = models.mobilenet_v3_small(weights=None)


num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, len(class_names))


try:
    model.load_state_dict(torch.load('production_mobilenet_weights.pth', map_location=device))
    model.eval()
    print("Custom MobileNet AI Model loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load custom weights. {e}")


inference_transforms = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


async def fire_webhook(incident_id: str, priority: str):
    """Sends an asynchronous REST API payload to the target system."""
    payload = {
        "incident_id": incident_id,
        "priority_level": priority,
        "status": "pending_dispatch"
    }
    
    # Pointing to our own simulated receiver for the demo
    webhook_target_url = "http://127.0.0.1:8000/api/webhook-receiver"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook_target_url, json=payload)
            print(f"Webhook fired asynchronously. Target responded with: {response.status_code}")
        except Exception as e:
            print(f"Webhook dispatch failed: {e}")


@app.post("/api/triage")
async def triage_incident(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = inference_transforms(image).unsqueeze(0)
    
    with torch.no_grad():
        
        outputs = model(input_tensor)

        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        
        safe_prob = probabilities[0].item()
        critical_prob = probabilities[1].item()
        
    
        if critical_prob >= 0.30:
            priority = "Critical"
            display_confidence = critical_prob 
        else:
            priority = "Safe"
            display_confidence = safe_prob 
            

    log_file = "dispatch_log.json"
    total_incidents = 0
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        with open(log_file, "r") as f:
            try:
                total_incidents = len(json.load(f))
            except:
                pass
                
    incident_id = f"REP-{(total_incidents + 1):03d}"
    background_tasks.add_task(fire_webhook, incident_id, priority)
    
    return {
        "message": "Upload successful. Triage complete.",
        "incident_id": incident_id,
        "priority": priority,
        "confidence": f"{display_confidence*100:.1f}%", 
        "dispatch_status": "Webhook queued"
    }


@app.post("/api/webhook-receiver")
async def receive_webhook(request: Request):
    payload = await request.json()
    log_file = "dispatch_log.json"
    lock_file = "dispatch_log.json.lock"
    
    with FileLock(lock_file, timeout=5):
        data = []
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            with open(log_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass
                
        data.insert(0, payload) 
        
        with open(log_file, "w") as f:
            json.dump(data, f, indent=4)
            
    return {"status": "Webhook payload securely logged"}