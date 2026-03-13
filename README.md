# 🚨 Central Dispatch: AI-Powered Animal Rescue Triage

An end-to-end, asynchronous microservice architecture designed to automate incident triage for animal rescue centers. 

This system allows field reporters to upload images of strays in distress. A custom-trained PyTorch computer vision model evaluates the the injury and utilizes a highly reusable webhook framework to instantly push critical alerts to a decoupled Streamlit dispatch dashboard.

## 🧠 System Architecture & Webhook Framework
The application is split into three distinct microservices running concurrently:

1. **FastAPI Inference Server (Backend):** Handles asynchronous image uploads, executes the deep learning model, and manages the data pipeline.
2. **Citizen Reporting Portal (Frontend 1):** A user-centric Streamlit interface for image capture and submission.
3. **Central Dispatch Dashboard (Frontend 2):** An interactive, real-time command center for volunteer dispatchers.

**The Asynchronous Webhook Engine:**
To prevent the AI inference from bottlenecking the UI, the system utilizes an asynchronous REST API webhook framework. When the FastAPI server finishes classifying an image, it immediately returns a `200 OK` tracking ID to the citizen. In the background (`BackgroundTasks`), it securely opens an enterprise Mutex (FileLock) and pushes the payload to the Central Dispatch log, allowing the dispatch UI to auto-refresh and display the new ticket without dropping database connections.

## 🔬 AI & Machine Learning Methodology
The core intelligence is powered by **MobileNetV3**, chosen specifically for its lightweight architecture (~2.5M parameters) to prevent overfitting on micro-datasets while remaining highly performant for edge deployment.

* **Training Data:** Curated custom dataset of healthy and visibly injured local strays. 
* **Validation Strategy:** Implemented **Stratified 5-Fold Cross-Validation** to ensure statistical reliability across the small dataset, locking in an 88.7% baseline accuracy.
* **Gradual Unfreezing:** The model was trained in two phases—first training the custom classification head, followed by unfreezing the deep convolutional features to learn specific trauma textures.
* **Dynamic Threshold Tuning for Recall:** In medical triage, False Negatives cost lives. The inference pipeline features a custom threshold mechanism (lowered to 30%) to aggressively prioritize Recall, ensuring edge-case injuries are successfully flagged for human review.

🔗 **[View the PyTorch Training Notebook (Google Colab)](https://colab.research.google.com/drive/17H9Zf7LdppxrQL0WVG7qVxF99rPwG_YC?usp=sharing)**

## 🚀 Tech Stack
* **Deep Learning:** PyTorch, Torchvision (MobileNetV3, v2 Augmentations)
* **Backend:** FastAPI, Uvicorn, Python `asyncio`
* **Frontend:** Streamlit, Pandas
* **Infrastructure:** Docker, Docker Compose, AWS EC2

## 🛠️ Local Installation & Deployment

### Prerequisites
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/rescue-ai-system.git](https://github.com/YOUR_USERNAME/rescue-ai-system.git)
cd rescue-ai-system
