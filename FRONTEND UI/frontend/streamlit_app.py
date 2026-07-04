"""
Streamlit frontend for the Personalized Networking Assistant.

Run with:
    streamlit run frontend/streamlit_app.py

Assumes the FastAPI backend is running at BACKEND_URL (default localhost:8000).
"""
import os
import streamlit as st
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Personalized Networking Assistant", page_icon="🤝", layout="centered")
st.title("🤝 Personalized Networking Assistant")
st.caption("Smart conversation starters, quick fact-checks, and a record of what actually worked.")

user_id = st.sidebar.text_input("Your name / ID", value="anonymous")

tab1, tab2, tab3 = st.tabs(["✨ Generate Starters", "🔍 Fact Check", "🕘 History"])

# --- Scenario 1: Generating Smart Starters -----------------------------------
with tab1:
    st.subheader("Generate Smart Starters")
    event_description = st.text_input("Event description", placeholder="AI for Sustainable Cities")
    interests_raw = st.text_input("Your interests (comma-separated)", placeholder="climate change, urban planning")

    if st.button("Generate starters", type="primary"):
        if not event_description.strip():
            st.warning("Please enter an event description.")
        else:
            interests = [i.strip() for i in interests_raw.split(",") if i.strip()]
            with st.spinner("Extracting themes and generating starters..."):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/starters/generate",
                        json={
                            "event_description": event_description,
                            "interests": interests,
                            "user_id": user_id,
                        },
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    st.success("Here's what I put together:")
                    st.markdown("**Detected themes:** " + ", ".join(data["themes"]))
                    st.markdown("**Conversation starters:**")
                    for i, starter in enumerate(data["starters"], start=1):
                        st.markdown(f"{i}. {starter}")

                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend: {exc}")

# --- Scenario 2: Quick Fact Verification -------------------------------------
with tab2:
    st.subheader("Quick Fact Verification")
    query = st.text_input("What do you want to fact-check?", placeholder="blockchain in healthcare")

    if st.button("Check fact"):
        if not query.strip():
            st.warning("Please enter something to check.")
        else:
            with st.spinner("Looking this up on Wikipedia..."):
                try:
                    resp = requests.post(f"{BACKEND_URL}/factcheck/query", json={"query": query}, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()

                    if data["found"]:
                        st.success(data["summary"])
                        if data.get("source_url"):
                            st.markdown(f"[Read more on Wikipedia]({data['source_url']})")
                    else:
                        st.info(data["summary"])

                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend: {exc}")

# --- Scenario 3: Reviewing Past Strategies -----------------------------------
with tab3:
    st.subheader("Review Past Strategies")

    if st.button("Refresh history"):
        st.session_state["_refresh"] = True

    try:
        resp = requests.get(f"{BACKEND_URL}/history/", params={"user_id": user_id}, timeout=30)
        resp.raise_for_status()
        history = resp.json()
    except requests.RequestException as exc:
        history = []
        st.error(f"Could not reach the backend: {exc}")

    if not history:
        st.info("No history yet. Generate some starters first!")

    for entry in history:
        with st.expander(f"{entry['event_description']} — {entry['timestamp'][:19].replace('T', ' ')}"):
            st.markdown("**Interests:** " + (", ".join(entry["interests"]) or "—"))
            st.markdown("**Themes:** " + ", ".join(entry["themes"]))
            st.markdown("**Starters:**")
            for i, s in enumerate(entry["starters"], start=1):
                st.markdown(f"{i}. {s}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Useful", key=f"up_{entry['id']}"):
                    requests.post(f"{BACKEND_URL}/history/feedback",
                                  json={"history_id": entry["id"], "useful": True}, timeout=10)
                    st.rerun()
            with col2:
                if st.button("👎 Not useful", key=f"down_{entry['id']}"):
                    requests.post(f"{BACKEND_URL}/history/feedback",
                                  json={"history_id": entry["id"], "useful": False}, timeout=10)
                    st.rerun()

            if entry["feedback"] is not None:
                st.caption("Marked: " + ("👍 Useful" if entry["feedback"] else "👎 Not useful"))
