import streamlit as st
import requests
from datetime import datetime
from sync import Sync
from sync.common import Audio, Video, GenerationOptions

# ---------------------------
# 设置 API 密钥和上传 API 密钥
# ---------------------------
API_KEY = st.secrets["API_KEY"]
UPLOAD_IO_API_KEY = st.secrets["UPLOAD_IO_API_KEY"]
BASE_UPLOAD_URL = "https://api.upload.io/v2/accounts/W23MTBr/uploads/binary"  # 替换为你的 Upload.io 账户 ID

# ---------------------------
# 支持的语言选项
# ---------------------------
LANGUAGES = {
    "英语 (English)": "en",
    "中文 (Chinese)": "zh",
    "日语 (Japanese)": "ja",
    "韩语 (Korean)": "ko",
    "西班牙语 (Spanish)": "es",
    "法语 (French)": "fr",
    "德语 (German)": "de",
    "意大利语 (Italian)": "it",
    "葡萄牙语 (Portuguese)": "pt"
}

# ---------------------------
# 上传文件到 Upload.io
# ---------------------------
def upload_to_uploadio(file):
    files = {'file': (file.name, file, file.type)}
    headers = {
        "Authorization": f"Bearer {UPLOAD_IO_API_KEY}"
    }
    response = requests.post(BASE_UPLOAD_URL, files=files, headers=headers)
    if response.status_code == 200:
        return response.json()["fileUrl"]
    else:
        st.error(f"上传失败: {response.text}")
        return None

# ---------------------------
# 页面标题和说明
# ---------------------------
st.set_page_config(page_title="Sync.so 视频生成器", layout="wide")
st.title("🎬 Sync.so 视频生成器")

# ---------------------------
# 选择参数
# ---------------------------
with st.sidebar:
    st.header("参数设置")
    model = st.selectbox("模型选择", ["lipsync-2"])
    selected_lang_label = st.selectbox("语言", list(LANGUAGES.keys()))
    language = LANGUAGES[selected_lang_label]
    voice = st.text_input("语音名称 (例如 onyx)", value="onyx")
    style = st.text_input("风格 (例如 default)", value="default")
    sync_mode = st.selectbox("同步模式", ["default", "accurate", "fast", "loop"])

# ---------------------------
# 上传视频/音频
# ---------------------------
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("上传视频 (mp4)", type=["mp4"])
with col2:
    audio_file = st.file_uploader("上传音频或文本 (mp3/wav/txt)", type=["mp3", "wav", "txt"])

# ---------------------------
# 提交生成
# ---------------------------
if st.button("🚀 开始生成"):
    if not video_file or not audio_file:
        st.warning("请上传视频和音频/文本文件！")
    else:
        with st.spinner("上传中..."):
            video_url = upload_to_uploadio(video_file)
            input_type = "audio" if audio_file.type.startswith("audio") else "text"

            if input_type == "audio":
                audio_url = upload_to_uploadio(audio_file)

        if video_url and (input_type == "audio" and audio_url or input_type == "text"):
            try:
                client = Sync(api_key=API_KEY)

                if input_type == "audio":
                    inputs = [
                        Video(url=video_url),
                        Audio(url=audio_url)
                    ]
                else:
                    text = audio_file.getvalue().decode("utf-8")
                    inputs = [
                        Video(url=video_url),
                        Audio(
                            text=text,
                            provider={"name": "elevenlabs", "voiceId": voice}
                        )
                    ]

                result = client.generations.create(
                    input=inputs,
                    model=model,
                    options=GenerationOptions(
                        sync_mode=sync_mode,
                        language=language,
                        voice=voice,
                        style=style
                    )
                )

                st.success("✅ 提交成功！")
                st.json(result.model_dump())

            except Exception as e:
                st.error(f"❌ 提交失败: {e}")
