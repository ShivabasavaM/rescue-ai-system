import streamlit as st
import requests
from PIL import Image
import os
BACKEND_URL = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL","http://127.0.0.1:8000")

st.set_page_config(page_title="Citizen Dogs Rescue Portal", page_icon="🐾", layout="centered")

st.title("🐾 Community Dogs Rescue Portal")
st.markdown("<h4 style='text-align: center;'>Report a Dog in Distress -- Help and Save Lives</h4>", 
    unsafe_allow_html=True)
st.info("Upload the Dogs Picture, Our AI will report the Volunteers based on the Status")

st.divider()

uploaded_file = st.file_uploader("Capture or upload Image(only JPG/JPEG/PNG allowed)", type=['jpeg','jpg','png'])

if uploaded_file is not None:
    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        MAX_SIZE_MB = 5
        is_valid = True
        if uploaded_file.size > MAX_SIZE_MB * 1024 *1024:
            st.error(f"Image is too large, upload of max {MAX_SIZE_MB}")
            is_valid = False
        elif uploaded_file.type not in ["image/jpeg","image/png"]:
            st.error(f"Only PNG and JPEG images are supported")
            is_valid = False
        else:
            st.markdown("**Image Preview**")
            st.image(uploaded_file, use_container_width=True)
        
        

    with col2:
        st.markdown("**Incident Action**")
        st.write("Please make sure that Uploaded image is clearly visible")

        if st.button("Submit Report", disabled= not is_valid or st.session_state.get("submitting", False), use_container_width=True, type="primary"):
            with st.spinner("AI is assessing the Dog's Image..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                try:
                    response = requests.post(f"{BACKEND_URL}/api/triage", files=files, timeout=15)
                    response.raise_for_status()
                    data = response.json()

                    priority = data.get("priority", "Unknown")
                    confidence = data.get("confidence", "N/A")
                    inc_id = data.get("incident_id","N/A")

                    st.success(f"Report Submitted Successfully!")
                    st.metric("Priority",priority, delta =f"Confidence: {confidence}")
                    st.code(f"Tracking ID: {inc_id}")

                except requests.exceptions.Timeout:
                    st.error("The Server is busy, Please try again after sometime")
                except requests.exceptions.ConnectionError:
                    st.error("Couldn't reach the Server")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Server returned as error : {e.response.status_code}")
                except (ValueError, KeyError):
                    st.error("Recieved an unexpected response from the server")

                finally:
                    st.session_state.submitting = False



