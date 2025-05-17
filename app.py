import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="ADS团队专用 同步口型生成器", layout="wide")

API_KEY = os.environ.get("API_KEY") or st.secrets.get("API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://api.sync.so/api/generate"

# 模型、声音、风格、语言等默认选项
MODELS = [
    "lipsync-2", "lipsync-1.9.0-beta", "lipsync-1.8.0",
    "lipsync-1.7.1", "lipsync-1.6.0"
]
VOICES = ["onyx", "shimmer", "echo"]
STYLES = ["default", "narration", "conversational"]
LANGUAGES = ["en", "zh", "es", "fr", "de"]

st.title("🎬 Sync.so 同步口型生成器")

st.sidebar.header("🗂 上传媒体文件")
video_file = st.sidebar.file_uploader("上传视频文件（mp4, mov）", type=["mp4", "mov"])
audio_file = st.sidebar.file_uploader("上传音频文件（mp3, wav）", type=["mp3", "wav"])
subtitle_file = st.sidebar.file_uploader("上传字幕文件（可选，srt 或 vtt）", type=["srt", "vtt"])

st.sidebar.header("⚙️ 生成参数设置")
model = st.sidebar.selectbox("选择模型", MODELS)
voice = st.sidebar.selectbox("选择声音", VOICES)
style = st.sidebar.selectbox("选择风格", STYLES)
language = st.sidebar.selectbox("选择语言", LANGUAGES)
sync_mode = st.sidebar.selectbox("同步模式", ["default", "loop"])
webhook_url = st.sidebar.text_input("回调Webhook地址（可选）")

def 模拟上传(file):
    # 这里演示用，实际部署时替换为真实文件上传代码（上传后返回URL）
    return f"https://example.com/{file.name}"

if st.sidebar.button("🚀 开始生成"):
    if not video_file or not audio_file:
        st.error("请上传视频和音频文件！")
    else:
        with st.spinner("上传文件并提交生成任务中..."):
            video_url = 模拟上传(video_file)
            audio_url = 模拟上传(audio_file)
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
                st.success(f"✅ 生成任务已启动，任务ID：{job_id}")
            else:
                st.error(f"❌ 生成任务提交失败，错误信息：{res.text}")

st.divider()
st.subheader("📄 生成任务列表")

查询关键词 = st.text_input("🔍 通过任务ID搜索")
当前页码 = st.number_input("分页页码", min_value=1, step=1, value=1)

params = {"page": 当前页码}
if 查询关键词:
    params["search"] = 查询关键词

response = requests.get(f"{BASE_URL}/list", headers=HEADERS, params=params)
if response.status_code == 200:
    jobs = response.json().get("items", [])
    总数 = response.json().get("total", 0)
    st.write(f"共查询到 {总数} 条任务记录，当前显示第 {当前页码} 页")

    for job in jobs:
        with st.expander(f"🧾 任务ID: {job['id']} | 状态: {job['status']}"):
            st.write(f"**模型名称：** {job['model']}")
            创建时间 = datetime.fromisoformat(job['createdAt']).strftime("%Y-%m-%d %H:%M:%S")
            st.write(f"**创建时间：** {创建时间}")
            st.write("**输入参数：**")
            st.json(job.get("input", {}))
            st.write("**生成选项：**")
            st.json(job.get("options", {}))

            if job.get("output") and job["output"].get("video"):
                st.video(job["output"]["video"])
                st.download_button("⬇️ 下载生成视频", job["output"]["video"], file_name=f"{job['id']}.mp4")
            else:
                st.info("⏳ 视频尚未生成完成")

            if st.button(f"🗑 删除任务 {job['id']}"):
                del_res = requests.delete(f"{BASE_URL}/delete/{job['id']}", headers=HEADERS)
                if del_res.status_code == 200:
                    st.success("删除成功，请刷新页面查看更新")
                else:
                    st.error("删除失败，请稍后重试")
else:
    st.error("❌ 无法获取生成任务列表")

