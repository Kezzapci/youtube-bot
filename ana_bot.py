import os, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB ACTIONS (LINUX) AYARI
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

# DOSYALAR
SOZLER_DOSYASI = "rusca_sozler.txt"
BASLIKLAR_DOSYASI = "youtube_basliklari.txt"
ACIKLAMALAR_DOSYASI = "youtube_aciklamalari.txt"
VIDEO_DOSYASI = "Wolf_Motivation_Video_y9oxsx15.mp4"
PROGRESS_FILE = "siradaki_soz.txt"

def veriyi_hazirla():
    # 1. Sıra Takibi (Yoksa sıfırdan başla)
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f: f.write("0")
    
    with open(PROGRESS_FILE, "r") as f:
        try:
            index = int(f.read().strip())
        except:
            index = 0

    # 2. Dosyaları Satır Satır Oku
    def oku(yol):
        with open(yol, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.readlines() if l.strip()]

    soz_listesi = oku(SOZLER_DOSYASI)
    baslik_listesi = oku(BASLIKLAR_DOSYASI)
    aciklama_listesi = oku(ACIKLAMALAR_DOSYASI)

    # 3. Sıradaki Veriyi Seç
    if index >= len(soz_listesi):
        index = 0 # Liste biterse en başa dön

    return {
        "soz": soz_listesi[index].upper(), # Videoya SADECE bu yazılacak (Sayı yok!)
        "baslik": baslik_listesi[index],
        "aciklama": ac_listesi[index] if index < len(aciklama_listesi) else "",
        "sonraki_index": index + 1
    }

if __name__ == "__main__":
    data = veriyi_hazirla()
    print(f"🚀 {data['sonraki_index']}. sıradaki video hazırlanıyor...")

    # Video İşleme
    clip = VideoFileClip(VIDEO_DOSYASI)
    
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)

    # VİDEO ÜSTÜNE YAZI (Sadece söz, sayı falan asla yok)
    txt = TextClip(
        data['soz'], 
        fontsize=65, 
        color='white', 
        font='DejaVu-Sans-Bold', 
        method='caption', 
        size=(clip.w * 0.8, None), 
        align='center'
    ).set_duration(clip.duration).set_position('center')

    final = CompositeVideoClip([clip, txt])
    final.write_videofile("yukle.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YouTube'a Bas
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as t: 
            creds = pickle.load(t)
        yt = build('youtube', 'v3', credentials=creds)

        body = {
            'snippet': {
                'title': data['baslik'], 
                'description': data['aciklama'], 
                'categoryId': '27', 
                'defaultLanguage': 'ru'
            },
            'status': {'privacyStatus': 'public'}
        }
        
        media = MediaFileUpload("yukle.mp4", chunksize=-1, resumable=True)
        yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
        
        # Sırayı bir artır ve kaydet
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(data['sonraki_index']))
            
        print("✅ İşlem tamam, sıra kaydedildi.")
    else:
        print("❌ token.json dosyası eksik!")
