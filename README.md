# 🐾 Rescue AI: Cloud-Native Incident Response System

A scalable, real-time AI-powered surveillance and triage platform designed for **animal welfare and rescue operations**.

This system follows a **microservices architecture** with a **webhook-driven workflow**, where citizen reports automatically trigger AI classification and volunteer dispatch.

---

## 🚀 Live Deployment

- 🔗 **Citizen Reporting Portal**  
  https://citizen-app.streamlit.app/  
  *Submit incidents with images*

- 🔗 **Volunteer Dispatch Dashboard**  
  https://volunteer-dashboard.streamlit.app/  
  *Monitor and respond to incidents in real time*

- 🧠 **AI Inference Engine**  
  Hosted on AWS EC2 (Ubuntu)

---

## 🏗️ Architecture Overview

The system is designed as a **decoupled, scalable ecosystem**:

### 1. Citizen App (Frontend)
- Built with Streamlit
- Captures incident details + images
- Sends data via **POST requests** to backend

### 2. AI Backend (Core Engine)
- Built with FastAPI (Uvicorn)
- Deployed on AWS EC2
- Uses **MobileNetV3 (PyTorch)** for real-time image classification
- Outputs:
  - `Critical` 🚨
  - `Safe` ✅

### 3. Volunteer Dashboard (Frontend)
- Real-time monitoring UI
- Fetches processed incidents from database
- Enables **one-click dispatch**

---

## 🛠️ Tech Stack

| Category        | Technologies |
|----------------|-------------|
| Language       | Python 3.12 |
| AI/ML          | PyTorch, Torchvision (MobileNetV3) |
| Backend        | FastAPI, Uvicorn, SQLite |
| Frontend       | Streamlit |
| Cloud/DevOps   | AWS EC2 (Ubuntu), Streamlit Cloud |
| Networking     | REST APIs, AWS Security Groups |
| Repo Structure | Monorepo (GitHub) |

---

## ⚙️ Local Setup

Follow these steps to run the full system locally:

### 1️⃣ Clone Repository
```bash
git clone https://github.com/ShivabasavaM/rescue-ai-system.git
cd rescue-ai-system

### 2️⃣ Start AI Backend
cd model
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

### 3️⃣ Start Citizen App (New Terminal)
cd citizen-app
python3 -m venv cenv
source cenv/bin/activate
pip install -r requirements.txt
streamlit run app.py

### 4️⃣ Start Volunteer Dashboard (New Terminal)
cd volunteer-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
