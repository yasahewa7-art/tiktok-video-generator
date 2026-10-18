import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from moviepy.editor import VideoFileClip, AudioFileClip # මියුසික් එකතු කිරීමට

# 1. Streamlit Secrets හරහා ආරක්ෂිතව Google Gemini AI API සක්‍රීය කිරීම
# (GitHub එකට ඔබේ Key එක කෙලින්ම නොපෙනෙන නිසා මෙය කවදාවත් බ්ලොක් නොවේ)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="One-Click AI TikTok Generator v2", page_icon="🚀", layout="centered")
st.title("🎬 One-Click AI TikTok වීඩියෝ සාදන්නා (සංගීතය සහිතව)")
st.write("AI පිටපත්, සැබෑ ਰූපරාමු සහ පසුබිම් සංගීතය එකම ක්ලික් එකකින්!")

topic = st.text_input("වීඩියෝ මාතෘකාව (Topic):", placeholder="උදා: ලංකාවේ අමුතුම කෑම වර්ග 3ක්...")
bg_image = st.file_uploader("1. පසුබිම් පින්තූරය ඇතුළත් කරන්න (Image Upload):", type=["jpg", "png", "jpeg"])
bg_music = st.file_uploader("2. පසුබිම් සංගීතය ඇතුළත් කරන්න (MP3 Music Upload):", type=["mp3", "wav"])

if st.button("🚀 AI වීඩියෝව සකසන්න"):
    if not topic:
        st.error("කරුණාකර වීඩියෝව සඳහා මාතෘකාවක් ඇතුළත් කරන්න!")
    else:
        with st.spinner("🧠 AI මඟින් පිටපත ලියමින් පවතී..."):
            try:
                # නවතම gemini-1.5-flash මොඩල් එක භාවිතයෙන් සිංහල TikTok පිටපත් ලිවීම
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Write a short, engaging TikTok video caption in Sinhala text about '{topic}'. Keep it inside 3 very short punchy sentences separated by commas."
                response = model.generate_content(prompt)
                
                captions = [c.strip() for c in response.text.split(',') if c.strip()][:3]
                if len(captions) < 3:
                    captions = ["ඔන්න යාළුවනේ අද මම...", topic, "දැන්ම බලලා Share කරන්න!"]
                
                st.success(f"📝 AI පිටපත: {', '.join(captions)}")
                
                # වීඩියෝ Frame සෑදීමේ ක්‍රියාවලිය
                width, height = 720, 1280
                fps = 30
                duration_sec = 6
                temp_video = "temp_video.mp4"
                final_video = "tiktok_ai_music_video.mp4"
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
                font_path = "C:\\Windows\\Fonts\\iskpota.ttf" if os.path.exists("C:\\Windows\\Fonts\\iskpota.ttf") else "arial.ttf"
                font = ImageFont.truetype(font_path, 42)
                num_frames = duration_sec * fps
                
                for frame_idx in range(num_frames):
                    if bg_image is not None:
                        file_bytes = np.asarray(bytearray(bg_image.read()), dtype=np.uint8)
                        bg_rgb = cv2.imdecode(file_bytes, 1)
                        bg_rgb = cv2.resize(bg_rgb, (width, height))
                        bg_image.seek(0)
                    else:
                        hue = int((frame_idx * 2) % 180)
                        bg_hsv = np.zeros((height, width, 3), dtype=np.uint8)
                        bg_hsv[..., 0] = hue
                        bg_hsv[..., 1] = 180
                        bg_hsv[..., 2] = 120
                        bg_rgb = cv2.cvtColor(bg_hsv, cv2.COLOR_HSV2BGR)
                    
                    pil_img = Image.fromarray(cv2.cvtColor(bg_rgb, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 80))
                    
                    current_caption = captions[(frame_idx // (fps * 2)) % len(captions)]
                    text_w = draw.textlength(current_caption, font=font)
                    draw.text(((width - text_w) // 2, height // 2), current_caption, font=font, fill=(255, 255, 255))
                    
                    video.write(cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))
                    
                video.release()
                
                # 3. සෑදූ වීඩියෝවට සැබෑම සංගීතය (Audio) එකතු කිරීම
                if bg_music is not None:
                    with open("temp_audio.mp3", "wb") as f:
                        f.write(bg_music.getbuffer())
                    
                    video_clip = VideoFileClip(temp_video)
                    audio_clip = AudioFileClip("temp_audio.mp3").subclip(0, duration_sec)
                    
                    final_clip = video_clip.set_audio(audio_clip)
                    final_clip.write_videofile(final_video, codec="libx264", audio_codec="aac")
                    
                    video_clip.close()
                    audio_clip.close()
                else:
                    os.rename(temp_video, final_video)
                
                st.success("🎉 සංගීතය සහිත AI වීඩියෝව සාදා නිමයි!")
                with open(final_video, "rb") as file:
                    st.download_button(
                        label="📥 සාදාගත් AI වීඩියෝව ඩවුන්ලෝඩ් කරගන්න",
                        data=file,
                        file_name="tiktok_ai_music_video.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ ගැටලුවක් මතු විය: {str(e)}")
