import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"  # or your server URL

st.title("📄 Resume Review Uploader")

# Upload Section
st.header("Upload your resume")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

if uploaded_file:
    if st.button("Upload"):
        with st.spinner("Uploading..."):
            response = requests.post(
                f"{API_BASE_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file,
                                uploaded_file.type)}
            )
        if response.status_code == 200:
            file_id = response.json().get("file_id")
            st.success(f"File uploaded successfully! File ID: `{file_id}`")
            st.session_state["last_file_id"] = file_id
        else:
            st.error("Upload failed!")

# Check Status
st.header("Check Resume Review Status")
file_id_input = st.text_input("Enter File ID", 
                              value=st.session_state.get("last_file_id", ""))

if st.button("Check Status"):
    if not file_id_input.strip():
        st.warning("Please enter a valid file ID.")
    else:
        with st.spinner("Fetching status..."):
            response = requests.get(f"{API_BASE_URL}/{file_id_input.strip()}")
        if response.status_code == 200:
            data = response.json()
            st.subheader("📄 File Details")
            st.write(f"**Name:** {data['name']}")
            st.write(f"**Status:** {data['status']}")
            if data.get("reviews"):
                st.subheader("✅ Reviews")
                st.json(data["reviews"])
            else:
                st.info("Review not available yet. Please check back later.")
        else:
            st.error("File not found!")
