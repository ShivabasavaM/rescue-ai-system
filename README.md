# 🐾 Rescue AI: Cloud-Native Triage System

## Problem
In emergency situations involving stray or wild animals, traditional manual triage is slow and inefficient. Most citizen reporting tools rely on polling (constantly refreshing for updates), which introduces high latency and delays critical responses. This project solves the problem of slow emergency allocation by utilizing an event-driven architecture that automatically processes, classifies, and dispatches critical distress cases in real time.

## Approach
- **Model:** Fine-tuned `PyTorch MobileNetV3` image classification architecture, optimized for lightweight, low-latency CPU inference via transfer learning on a custom dataset.
- **Pipeline:** An end-to-end event-driven microservices pipeline running on decoupled architecture components.
- **Why this approach:** Using an event-driven POST request ensures the server only processes data when an incident occurs, saving compute and memory while enabling rapid processing within strict hardware limitations (1GB RAM on AWS Free Tier).

## Architecture
graph TD
    %% Styling Definitions
    classDef client fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#fff,rx:5px,ry:5px;
    classDef server fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff,rx:5px,ry:5px;
    classDef external fill:#1f2937,stroke:#9ca3af,stroke-width:2px,color:#fff,rx:5px,ry:5px;
    classDef db fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff,rx:15px,ry:15px;

    subgraph ClientLayer ["Client Layer"]
        UI["React / Vite UI<br/>(Vercel)"]:::client
    end

    subgraph ApplicationLayer ["Application Server Layer"]
        API["FastAPI Orchestrator<br/>(Render)"]:::server
        Threads["Parallel ThreadPool<br/>(8-Pillar Agentic Reasoning)"]:::server
        Buffer["io.BytesIO<br/>(.docx Memory Stream)"]:::server
    end

    subgraph InfrastructureLayer ["External AI & Data Infrastructure"]
        Llama["LlamaParse API<br/>(Document Extraction)"]:::external
        Gemini["Gemini 2.5 Flash<br/>(LLM & Embeddings)"]:::external
        Pinecone[("Pinecone Vector DB<br/>(Ephemeral Namespaces)")]:::db
    end

    %% Data Flow
    UI -- "1. Upload PDFs & Query" --> API
    
    API -- "2. Raw Documents" --> Llama
    Llama -- "3. Parsed Markdown" --> Gemini
    Gemini -- "4. Vector Embeddings" --> Pinecone
    
    API -- "5. Trigger Gap Analysis" --> Threads
    Threads <-->| "6. Context Retrieval" | Pinecone
    Threads <-->| "7. Verification Loop" | Gemini
    
    Threads -- "8. Audit Findings" --> Buffer
    Buffer -- "9. Stream Report" --> UI

## Results
- **Metrics:** Achieved an **88.7% accuracy** on the test dataset utilizing data augmentation and transfer learning.
- **Observations:** The model maintains a sub-second inference time and low memory footprint by disabling gradient computations via `torch.no_grad()`.

## Tradeoffs
- **What you optimized for:** Optimized for **low memory usage** and **high availability** within resource-constrained environments, utilizing a rolling window of 15 records in SQLite to conserve storage.

## Failures / Learnings
- **What didn't work:** Attempting to load heavy models like ResNet resulted in out-of-memory (OOM) failures on the `t3.micro` instance. 
- **Learnings:** Employing MobileNetV3 and configuring 2GB of Linux Swap memory stabilized the system. Understanding the practical differences between polling and push-based/event-driven requests led to a more reliable network design.

## Demo
- **[Citizen Reporting Portal](https://citizen-app.streamlit.app/)**
- **[Volunteer Dispatch Dashboard](https://volunteer-dashboard.streamlit.app/)**

## Manim Explanation 🎥
- ** Animation explaining the event-driven workflow. **

https://github.com/user-attachments/assets/58e1ee36-7c73-4c5b-80a4-7e7975e882ab

## How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/ShivabasavaM/rescue-ai-system.git](https://github.com/ShivabasavaM/rescue-ai-system.git)
cd rescue-ai-system
```
### 2. Start the AI Backend
```
cd model
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000 
```

### 3. Start the Citizen App
### Open a new terminal:
```
cd citizen-app
python3 -m venv cenv
source cenv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 4. Start the Volunteer Dashboard
## Open a third terminal:

```
cd volunteer-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py 
```
