import os
import cv2
import requests # ඉන්ටර්නෙට් එකෙන් පින්තූරය කියවීමට
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip

st.set_page_config(page_title="One-Click TikTok Video Generator", page_icon="🚀", layout="centered")
st.title("🎬 One-Click TikTok වීඩියෝ සාදන්නා (සම්පූර්ණ නිමාව)")
st.write("මාතෘකාවක් දෙන්න. එක ක්ලික් එකකින් සැබෑ වීඩියෝවක් ඔන්ලයින්ම සාදා බාගත කරගන්න!")

# පරිශීලකයාගෙන් තොරතුරු ලබාගැනීම
topic = st.text_input("වීඩියෝ මාතෘකාව (Topic):", placeholder="උදා: සීගිරිය (sigiriya)...")
bg_image = st.file_uploader("1. ඔබේම පසුබිම් පින්තූරයක් ඇතුළත් කරන්න (කැමති නම් පමණක්):", type=["jpg", "png", "jpeg"])
bg_music = st.file_uploader("2. පසුබිම් සංගීතය ඇතුළත් කරන්න (MP3 Music Upload):", type=["mp3", "wav"])

if st.button("🚀 වීඩියෝව සකසන්න (Generate Video)"):
    if not topic:
        st.error("kisi wachanayak dunne ne!")
    else:
        with st.spinner("⏳ වීඩියෝව සකස් වෙමින් පවතී, කරුණාකර තත්පර කිහිපයක් රැඳී සිටින්න..."):
            try:
                # කැප්ෂන්ස් ටික ලස්සනට සකස් කිරීම
                captions = [
                    f"Today we are talking about {topic}!",
                    "This is one of the most beautiful places.",
                    "Like and Share this video now!"
                ]
                
                # වීඩියෝ Frame සෑදීමේ ක්‍රියාවලිය (TikTok 9:16)
                width, height = 720, 1280
                fps = 30
                duration_sec = 6
                temp_video = "temp_video.mp4"
                final_video = "tiktok_final_video.mp4"
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
                # 1. පසුබිම් රූපය තෝරාගැනීම (Upload හෝ Online Default Image)
                if bg_image is not None:
                    file_bytes = np.asarray(bytearray(bg_image.read()), dtype=np.uint8)
                    bg_rgb = cv2.imdecode(file_bytes, 1)
                    bg_rgb = cv2.resize(bg_rgb, (width, height))
                    bg_image.seek(0)
                else:
                    # පරිශීලකයා පින්තූරයක් නොදුන්නොත් Unsplash හරහා සජීවීව ලස්සන සීගිරියේ පින්තූරයක් ලබාගනී
                    online_url = "https://unsplash.com"
                    try:
                        resp = requests.get(online_url, stream=True).raw
                        online_img = Image.open(resp).convert('RGB')
                        bg_rgb = cv2.cvtColor(np.array(online_img), cv2.COLOR_RGB2BGR)
                        bg_rgb = cv2.resize(bg_rgb, (width, height))
                    except:
                        # ඉන්ටර්නෙට් ගැටලුවක් ආවොත් ලස්සන Gradient පසුබිමක් සාදයි
                        bg_rgb = np.zeros((height, width, 3), dtype=np.uint8)
                        for y in range(height):
                            bg_rgb[y, :] = [180, 20, int(30 + (y/height)*80)]
                
                num_frames = duration_sec * fps
                
                for frame_idx in range(num_frames):
                    pil_img = Image.fromarray(cv2.cvtColor(bg_rgb, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    
                    # අකුරු හොඳින් පෙනීමට කළු තීරුවක් (Overlay) දැමීම
                    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 70))
                    
                    # උපසිරැසි කාලයට අනුව මාරු කිරීම (විශාලව සහ පැහැදිලිව පෙනීමට සකසා ඇත)
                    current_caption = captions[(frame_idx // (fps * 2)) % len(captions)]
                    
                    # Default Font එක විශාල කර පෙන්වීමට සරල ඇඳීමේ තාක්ෂණයක්
                    # (Linux සර්වර්ස්වල font size එක කෙලින්ම වෙනස් කළ නොහැකි නිසා PIL textoverlay මඟින් විශාල කර ඇත)
                    ctx = Image.new('RGBA', (width, height), (0,0,0,0))
                    d = ImageDraw.Draw(ctx)
                    d.text((40, height // 2), current_caption, fill=(255, 255, 0))
                    # Resize කර අකුරු විශාල කර පෙන්වීම
                    ctx = ctx.resize((width * 2, height * 2), Image.NEAREST)
                    pil_img.paste(ctx.resize((width, height)), (0, 0), ctx.resize((width, height)))
                    
                    video.write(cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))
                    
                video.release()
                
                # 3. පසුබිම් සංගීතය එකතු කිරීම
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
                    if os.path.exists(final_video):
                        os.remove(final_video)
                    os.rename(temp_video, final_video)
                
                st.success("🎉 ඔබේ TikTok වීඩියෝව සාර්ථකව සාදා නිමයි!")
                with open(final_video, "rb") as file:
                    st.download_button(
                        label="📥 සාදාගත් වීඩියෝව ඩවුන්ලෝඩ් කරගන්න",
                        data=file,
                        file_name="tiktok_video.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ ගැටලුවක් මතු විය: {str(e)}")
