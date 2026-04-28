import os, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB ACTIONS (LINUX) İÇİN IMAGEMAGICK AYARI
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

# REPO İÇİNDEKİ DOSYA ADLARI
SOZLER_DOSYASI = "rusca_sozler.txt"
BASLIKLAR_DOSYASI = "youtube_basliklari.txt"
ACIKLAMALAR_DOSYASI = "youtube_aciklamalari.txt"
VIDEO_DOSYASI = "Wolf_Motivation_Video_y9oxsx15.mp4"
PROGRESS_FILE = "siradaki_soz.txt"

def veri_getir():
    # Mevcut indeksi kontrol et ve oku
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f: f.write("0")
    
    with open(PROGRESS_FILE, "r") as f:
        content = f.read().strip()
        index = int(content) if content else 0

    # Dosyaları listeye çevir (boş satırları atla)
    with open(SOZLER_DOSYASI, "r", encoding="utf-8") as f: 
        sozler = [l.strip() for l in f.readlines() if l.strip()]
    with open(BASLIKLAR_DOSYASI, "r", encoding="utf-8") as f: 
        basliklar = [l.strip() for l in f.readlines() if l.strip()]
    with open(ACIKLAMALAR_DOSYASI, "r", encoding="utf-8") as f: 
        aciklamalar = [l.strip() for l in f.readlines() if l.strip()]

    # Liste sonuna gelindiyse başa dön
    if index >= len(sozler): index = 0

    return {
        "soz": sozler[index].upper(),
        "baslik": basliklar[index],
        "aciklama": aciklamalar[index],
        "yeni_index": index + 1
    }

if __name__ == "__main__":
    data = veri_getir()
    print(f"🎬 Hazırlanıyor: {data['baslik']}")

    if not os.path.exists(VIDEO_DOSYASI):
        print(f"❌ HATA: {VIDEO_DOSYASI} dosyası repo içinde bulunamadı!")
        exit(1)

    # Video Düzenleme Aşaması
    clip = VideoFileClip(VIDEO_DOSYASI)
    
    # Müzik varsa ekle (muzik.mp3 repoda olmalı)
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)
    
    # Metin klibi (Kalın punto ve Rusça karakter desteği için DejaVu-Sans-Bold)
    txt = TextClip(data['soz'], fontsize=65, color='white', font='DejaVu-Sans-Bold', 
                   method='caption', size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    
    final = CompositeVideoClip([clip, txt])
    output_name = "youtube_hazir.mp4"
    final.write_videofile(output_name, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YouTube API Yükleme
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as t: 
            creds = pickle.load(t)
        yt = build('youtube', 'v3', credentials=creds)

        body = {
            'snippet': {
                'title': data['baslik'], 
                'description': data['aciklama'], 
                'categoryId': '27', # Eğitim/Gelişim
                'defaultLanguage': 'ru'
            },
            'status': {'privacyStatus': 'public'}
        }
        
        media = MediaFileUpload(output_name, chunksize=-1, resumable=True)
        yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
        
        # Başarılı olursa indeksi güncelle
        with open(PROGRESS_FILE, "w") as f: f.write(str(data['yeni_index']))
        print(f"🚀 Video Başarıyla Yüklendi: {data['baslik']}")
    else:
        print("❌ HATA: YouTube token.json bulunamadı!")
        exit(1)
