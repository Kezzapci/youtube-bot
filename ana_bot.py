import os, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB ACTIONS (LINUX) AYARI
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

# DOSYA ADLARI
SOZLER_FILE = "rusca_sozler.txt"
BASLIKLAR_FILE = "youtube_basliklari.txt"
ACIKLAMALAR_FILE = "youtube_aciklamalari.txt"
VIDEO_DOSYASI = "Wolf_Motivation_Video_y9oxsx15.mp4"
PROGRESS_FILE = "siradaki_soz.txt"

def veri_cek():
    # Mevcut sırayı oku (Eğer dosya yoksa 0'dan başla)
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f: f.write("0")
    
    with open(PROGRESS_FILE, "r") as f:
        try:
            index = int(f.read().strip())
        except:
            index = 0

    # Tüm dosyaları satır satır listeye al
    def dosya_oku(dosya_adi):
        if not os.path.exists(dosya_adi):
            print(f"❌ KRİTİK HATA: {dosya_adi} bulunamadı!")
            return []
        with open(dosya_adi, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    sozler = dosya_oku(SOZLER_FILE)
    basliklar = dosya_oku(BASLIKLAR_FILE)
    aciklamalar = dosya_oku(ACIKLAMALAR_FILE)

    # Eğer liste biterse en başa dön
    if index >= len(sozler):
        index = 0

    # Her dosyadan aynı sıradaki veriyi çekiyoruz
    veri = {
        "soz": sozler[index].upper(),
        "baslik": basliklar[index] if index < len(basliklar) else "Motivación Diaria",
        "aciklama": aciklamalar[index] if index < len(aciklamalar) else "",
        "yeni_index": index + 1
    }
    return veri

if __name__ == "__main__":
    data = veri_cek()
    print(f"📌 Sıra: {data['yeni_index']} | Başlık: {data['baslik']}")

    # Video İşleme
    clip = VideoFileClip(VIDEO_DOSYASI)
    
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)
    
    # Metni videoya yaz (Kalın ve Rusça uyumlu font)
    txt = TextClip(data['soz'], fontsize=65, color='white', font='DejaVu-Sans-Bold', 
                   method='caption', size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    
    final = CompositeVideoClip([clip, txt])
    output = "son_video.mp4"
    final.write_videofile(output, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YouTube Yükleme
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
        
        media = MediaFileUpload(output, chunksize=-1, resumable=True)
        yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
        
        # SIRA GÜNCELLEME: Sadece yükleme başarılıysa indexi bir artırıp dosyaya yaz
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(data['yeni_index']))
            
        print(f"✅ Başarıyla yüklendi ve sıra {data['yeni_index']} olarak güncellendi.")
    else:
        print("❌ token.json yok, yükleme başarısız.")
