import streamlit as st
import pandas as pd 
import os
import time
import requests

BACKEND_URL = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL","http://127.0.0.1:8000")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL","30"))

st.set_page_config(page_title="Rescue Dispatch", page_icon="🏥", layout="wide")

st.title("Central Dispatch | Volunteers Triage System Dashboard")
st.warning("⚠️ **NOTICE:** This portal is a technical demonstration for a portfolio project. It is NOT connected to real emergency services. Please do not submit actual emergencies here.")
st.markdown("Live Incident Queue is displayed, please reach and rescue the Paws | Save lives")

st.divider()

def fetch_incidents() -> list[dict]:
    try:
        response = requests.get(f"{BACKEND_URL}/api/incidents", timeout=10)
        response.raise_for_status()
        return response.json().get("incidents",[])

    except requests.exceptions.ConnectionError:
        st.error("couldn't connect to the server try again after sometime")
        return []

    except requests.exceptions.Timeout:
        st.error("Server taking too long to respond, try again after sometime")
        return []

    except requests.exceptions.HTTPError as e:
        st.error(f"Server returned an error {e}")
        return []
    
    except Exception:
        st.error("Unexpected error while fetching incidents")
        return []

def dispatch_incident(incident_id:str) -> bool:
    try:
        response = requests.patch(f"{BACKEND_URL}/api/incidents/{incident_id}/dispatch", timeout=5)
        response.raise_for_status()
        return True

    except requests.exceptions.ConnectionError:
        st.error("Could not reach the server to dispatch the unit.")
        return False

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"Incident ID - {incident_id} not found")
            return False
        else:
            st.error(f"Dispatch failed : {e.response.status_code}")
            return False
    except Exception:
        st.error("Unexpected error during dispatch.")
        return False

all_incidents = fetch_incidents()

active_incidents = [i for i in all_incidents if i.get("status")!="dispatched"]
history_incidents = [i for i in all_incidents if i.get("status")=="dispatched"]

critical_count = sum(1 for i in active_incidents if i.get("priority")=="critical")
safe_count = sum(1 for i in active_incidents if i.get("priority")=="safe")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Active Incidents", len(active_incidents))
with col2:
    st.metric("🔴 Critical (Pending)", critical_count)
with col3:
    st.metric("🟢 Safe (Pending)", safe_count)
with col4:
    st.metric("✅ Dispatched", len(history_incidents))

st.divider()

tab1, tab2 = st.tabs(["🚨 Active Incidents", "📜 Dispatch History"])

with tab1:
    if not active_incidents:
        st.success("No Active incidents. All clear!")
    else:
        st.markdown(f"**{len(active_incidents)} incident(s) awaiting dispatch**")
        sorted_active = sorted(
            active_incidents,
            key = lambda x :(
                0 if x.get("priority", "").lower() == "critical" else 1,
                x.get("timestamp", "")
            )
        )

        for incident in sorted_active:
            inc_id = incident.get("incident_id", "N/A")
            priority = incident.get("priority","Unkown")
            confidence = incident.get("confidence","N/A")
            status = incident.get("status","N/A")
            timestamp = incident.get("timestamp","N/A")

            is_critical = priority.lower() == "critical"
            border_color = "#E24B4A" if is_critical else "#1D9E75"
            priority_emoji = "🔴" if is_critical else "🟢"

            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([1.5,1.5,1.2,1.5,1.5])
                with c1:
                    st.markdown(f"**Incident ID**")
                    st.code(inc_id)
                with c2:
                    st.markdown(f"**Priority**")
                    st.markdown(f"{priority_emoji} **{priority}**")
                with c3:
                    st.markdown(f"**confidence**")
                    st.write(confidence)
                with c4:
                    st.markdown(f"**Reported At**")
                    st.write(timestamp)
                with c5:
                    st.markdown("**Action**")
                    if st.button("Dispatch Unit",
                    key=f"dispatch_{inc_id}",
                    type="primary" if is_critical else "secondary",
                    use_container_width=True,
                    ):
                        with st.spinner(f"Volunteer is being assigned to {inc_id}"):
                            success = dispatch_incident(inc_id)
                        if success:
                            st.success(f"Volunteer assigned to {inc_id}!")
                            time.sleep(1)
                            st.rerun()


with tab2:
    if not history_incidents:
        st.info("No dispatched incidents yet.")
    else:
        st.markdown(f"**{len(history_incidents)} dispatch incident(s)**")

        df = pd.DataFrame(history_incidents)

        display_cols = {
            "incident_id" : "Incident Id",
            "priority" : "Priority",
            "confidence" : "Confidence",
            "status" : "Status",
            "timestamp" : "Timestamp",
        }
        existing = {k: v for k, v in display_cols.items() if k in df.columns}
        df = df[list(existing.keys())].rename(columns=existing)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # csv = df.to_csv(index=False).encode("utf-8")
        # st.download_button(
        #     label="⬇️ Download Log as CSV",
        #     data = csv,
        #     file_name = "dispatch_history.csv",
        #     mime="text/csv",
        # )

st.divider()

refresh_col, status_col = st.columns([1,3])

with refresh_col:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

with status_col:
    st.caption(f"Dashboard auto-refreshes every {REFRESH_INTERVAL} seconds.")

time.sleep(REFRESH_INTERVAL)
st.rerun()
