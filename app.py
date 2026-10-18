import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip

st.set_page_config(page_title="One-Click TikTok Video Generator", page_icon="🚀", layout="centered")
st.title("🎬 One-Click TikTok වීඩියෝ සාදන්නා (100% සජීවීව)")
st.write("මාතෘකාවක් දෙන්න. එක ක්ලික් එකකින් සැබෑ වීඩියෝවක් ඔන්ලයින්ම සාදා බාගත කරගන්න!")

# පරිශීලකයාගෙන් තොරතුරු ලබාගැනීම
topic = st.text_input("වීඩියෝ මාතෘකාව (Topic):", placeholder="උදා: ලංකාවේ ලස්සනම තැන් 3ක්...")
bg_image = st.file_uploader("1. පසුබිම් පින්තූරය ඇතුළත් කරන්න (Image Upload):", type=["jpg", "png", "jpeg"])
bg_music = st.file_uploader("2. පසුබිම් සංගීතය ඇතුළත් කරන්න (MP3 Music Upload):", type=["mp3", "wav"])

if st.button("🚀 වීඩියෝව සකසන්න (Generate Video)"):
    if not topic:
        st.error("කරුණාකර වීඩියෝව සඳහා මාතෘකාවක් ඇතුළත් කරන්න!")
    else:
        with st.spinner("⏳ වීඩියෝව සකස් වෙමින් පවතී, කරුණාකර තත්පර කිහිපයක් රැඳී සිටින්න..."):
            try:
                # 404/401 දෝෂ සම්පූර්ණයෙන්ම නැති කිරීමට ස්වයංක්‍රීය සිංහල පිටපත් පද්ධතියක් සක්‍රීය කිරීම
                captions = [
                    f"අද ඔයාලට ගෙනාවේ {topic} ගැන විශේෂ වීඩියෝවක්!",
                    "කවුරුත් නොදන්න රහස් කිහිපයක් මෙන්න.",
                    "වීඩියෝව දිගටම බලලා යාලුවන්ටත් Share කරන්න!"
                ]
                
                st.success(f"📝 වීඩියෝ පිටපත සූදානම්!")
                
                # වීඩියෝ Frame සෑදීමේ ක්‍රියාවලිය (TikTok 9:16)
                width, height = 720, 1280
                fps = 30
                duration_sec = 6
                temp_video = "temp_video.mp4"
                final_video = "tiktok_final_video.mp4"
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
                # Linux සර්වර්ස්වල ඇතිවන 'cannot open resource' වැරැද්ද මඟහැරවීමට Default Font එක භාවිත කිරීම
                font = ImageFont.load_default()
                
                num_frames = duration_sec * fps
                
                for frame_idx in range(num_frames):
                    if bg_image is not None:
                        file_bytes = np.asarray(bytearray(bg_image.read()), dtype=np.uint8)
                        bg_rgb = cv2.imdecode(file_bytes, 1)
                        bg_rgb = cv2.resize(bg_rgb, (width, height))
                        bg_image.seek(0)
                    else:
                        # පින්තූරයක් නැත්නම් ලස්සන වර්ණවත් පසුබිමක් සෑදීම
                        hue = int((frame_idx * 2) % 180)
                        bg_hsv = np.zeros((height, width, 3), dtype=np.uint8)
                        bg_hsv[..., 0] = hue
                        bg_hsv[..., 1] = 180
                        bg_hsv[..., 2] = 100
                        bg_rgb = cv2.cvtColor(bg_hsv, cv2.COLOR_HSV2BGR)
                    
                    pil_img = Image.fromarray(cv2.cvtColor(bg_rgb, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    
                    # අකුරු හොඳින් පෙනීමට කළු තීරුවක් (Overlay) දැමීම
                    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 70))
                    
                    # උපසිරැසි කාලයට අනුව මාරු කිරීම
                    current_caption = captions[(frame_idx // (fps * 2)) % len(captions)]
                    text_w = draw.textlength(current_caption, font=font)
                    draw.text(((width - text_w) // 2, height // 2), current_caption, font=font, fill=(255, 255, 255))
                    
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
