import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Citizen Rescue Portal", page_icon="🐾", layout="centered")

st.title("🐾 Community Rescue Portal")
st.markdown("### Help us save lives. Report an animal in distress.")
st.info("Upload a photo of the stray animal. Our AI will instantly assess the severity and alert the nearest rescue team in the area.", icon="ℹ️")

st.divider()

uploaded_file = st.file_uploader("Capture or upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        st.markdown("**Image Preview**")
        st.image(uploaded_file, use_container_width=True)
        
    with col2:
        st.markdown("**Incident Action**")
        st.write("Please ensure the animal is clearly visible before submitting.")
        
        if st.button("🚨 Submit Emergency Report", use_container_width=True, type="primary"):
            with st.spinner("AI assessing incident severity..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                try:
                    response = requests.post("http://127.0.0.1:8000/api/triage", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Report transmitted to Central Dispatch!", icon="✅")
                        st.metric(label="System Classification", value=data['priority'], delta=f"AI Confidence: {data['confidence']}")
                        st.code(f"Live Tracking ID: {data['incident_id']}")
                        
                        st.markdown("*A volunteer unit will be assigned shortly if the priority is Critical.*")
                    else:
                        st.error(f"Backend Error: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the Central Triage Server.")