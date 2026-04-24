import os, random, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB SİSTEM AYARI (Linux dizin yapısı)
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

def siradaki_sozu_al():
    prog_file = "siradaki_soz.txt"
    if not os.path.exists(prog_file):
        with open(prog_file, "w") as f: f.write("0")
    with open(prog_file, "r") as f:
        index = int(f.read().strip())
    
    with open("motivasyon_sozleri_1000.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if index >= len(lines): index = 0
    soz = lines[index].strip()
    
    with open(prog_file, "w") as f: f.write(str(index + 1))
    return soz.upper()

if __name__ == "__main__":
    soz = siradaki_sozu_al()
    
    # Depondaki video
    video_path = "video.mp4" 
    
    if not os.path.exists(video_path):
        print("❌ HATA: video.mp4 dosyası bulunamadı!")
        exit()

    clip = VideoFileClip(video_path).subclip(0, 10)
    
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)
    
    txt = TextClip(soz, fontsize=50, color='white', font='Arial-Bold', method='caption', 
                   size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    
    final = CompositeVideoClip([clip, txt])
    final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YOUTUBE YÜKLEME - KEŞFET ODAKLI DÜZENLEME
    with open('token.json', 'rb') as t: 
        creds = pickle.load(t)
    yt = build('youtube', 'v3', credentials=creds)

    # KEŞFET AYARLARI
    # Başlığın başına emoji ve "GÜNÜN MOTİVASYONU" ekleyerek dikkat çekiyoruz
    baslik = f"GÜNÜN MOTİVASYONU: {soz[:40]}... 🔥 #shorts"
    
    # Açıklamaya etkileşim sorusu ve geniş hashtag havuzu ekledik
    aciklama = (
        f"{soz}\n\n"
        "Zihnini her gün bir adım ileriye taşı! 💪✨\n\n"
        "Sence başarının sırrı nedir? Yorumlarda buluşalım! 👇\n\n"
        "Her gün yeni bir doz motivasyon için abone olmayı unutma! 🚀\n\n"
        "#motivasyon #başarı #disiplin #gelişim #psikoloji #keşfet #shorts #zihin"
    )

    body = {
        'snippet': {
            'title': baslik, 
            'description': aciklama, 
            'categoryId': '27', # '22' yerine '27' (Eğitim) kategorisi bu tarz içerikleri daha iyi keşfete sokar
            'defaultLanguage': 'tr'
        },
        'status': {'privacyStatus': 'public'}
    }
    
    media = MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
    yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
    print(f"🚀 Keşfet odaklı video paylaşıldı: {baslik}")
