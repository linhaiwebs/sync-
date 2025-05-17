# sync_generator_app/app.py
import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="Sync.so Generator", layout="wide")

# Load API Key
API_KEY = os.environ.get("API_KEY") or st.secrets.get("API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://api.sync.so/api/generate"

# Constants for dynamic dropdowns
DEFAULT_VOICES = ["onyx", "shimmer", "echo"]
DEFAULT_STYLES = ["default", "narration", "conversational"]
DEFAULT_LANGUAGES = ["en", "zh", "es", "fr", "de"]
MODELS = [
    "lipsync-2", "lipsync-1.9.0-beta", "lipsync-1.8.0", "lipsync-1.7.1", "lipsync-1.6.0"
]

st.title("🎬 Sync.so LipSync Generator")

# Sidebar: Upload section
st.sidebar.header("🗂 Upload Media")
video_file = st.sidebar.file_uploader("Upload Video", type=["mp4", "mov"])
audio_file = st.sidebar.file_uploader("Upload Audio", type=["mp3", "wav"])
subtitle_file = st.sidebar.file_uploader("Upload Subtitles (Optional)", type=["srt", "vtt"])

# Sidebar: Configuration section
st.sidebar.header("⚙️ Generation Settings")
model = st.sidebar.selectbox("Model", MODELS)
voice = st.sidebar.selectbox("Voice", DEFAULT_VOICES)
style = st.sidebar.selectbox("Style", DEFAULT_STYLES)
language = st.sidebar.selectbox("Language", DEFAULT_LANGUAGES)
sync_mode = st.sidebar.selectbox("Sync Mode", ["default", "loop"])

webhook_url = st.sidebar.text_input("Webhook URL (optional)")

# Upload files to a file hosting endpoint or pre-signed URL (for demo, simulate it)
def simulate_upload(file):
    # Replace this with actual cloud upload code
    return f"https://example.com/{file.name}"

# Submit generation job
if st.sidebar.button("🚀 Generate"):
    if not video_file or not audio_file:
        st.error("Please upload both video and audio files.")
    else:
        with st.spinner("Uploading files and submitting task..."):
            video_url = simulate_upload(video_file)
            audio_url = simulate_upload(audio_file)

            payload = {
                "model": model,
                "input": [
                    {"type": "video", "url": video_url},
                    {"type": "audio", "url": audio_url}
                ],
                "options": {
                    "sync_mode": sync_mode,
                    "voice": voice,
                    "style": style,
                    "language": language
                }
            }
            if webhook_url:
                payload["webhookUrl"] = webhook_url

            res = requests.post(f"{BASE_URL}/create", json=payload, headers=HEADERS)
            if res.status_code == 200:
                job_id = res.json().get("id")
                st.success(f"✅ Generation started! Job ID: {job_id}")
            else:
                st.error(f"❌ Failed to create generation: {res.text}")

st.divider()
st.subheader("📄 Generation Records")

# Pagination & Search
query = st.text_input("🔍 Search by Job ID")
page = st.number_input("Page", min_value=1, step=1, value=1)

params = {"page": page}
if query:
    params["search"] = query

response = requests.get(f"{BASE_URL}/list", headers=HEADERS, params=params)
if response.status_code == 200:
    jobs = response.json().get("items", [])
    total = response.json().get("total", 0)

    for job in jobs:
        with st.expander(f"🧾 Job {job['id']} | Status: {job['status']}"):
            st.write(f"**Model:** {job['model']}")
            st.write(f"**Created:** {datetime.fromisoformat(job['createdAt']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.json(job.get("input", {}))
            st.json(job.get("options", {}))
            
            if job.get("output"):
                st.video(job['output'].get("video"))
                st.download_button("Download Video", job['output']['video'], file_name=f"{job['id']}.mp4")
            else:
                st.info("⏳ Not ready yet.")

            # Optional delete button
            if st.button(f"🗑 Delete {job['id']}"):
                del_res = requests.delete(f"{BASE_URL}/delete/{job['id']}", headers=HEADERS)
                if del_res.status_code == 200:
                    st.success("Deleted successfully. Please refresh.")
                else:
                    st.error("Failed to delete.")
else:
    st.error("❌ Failed to fetch generation records.")
