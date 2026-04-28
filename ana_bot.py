import os, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB ACTIONS (LINUX) AYARI
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

# DOSYA YOLLARI (Repo kök dizini)
SOZLER_DOSYASI = "rusca_sozler.txt"
BASLIKLAR_DOSYASI = "youtube_basliklari.txt"
ACIKLAMALAR_DOSYASI = "youtube_aciklamalari.txt"
VIDEO_DOSYASI = "Wolf_Motivation_Video_y9oxsx15.mp4"
PROGRESS_FILE = "siradaki_soz.txt"

def guncel_veriyi_getir():
    # 1. Hangi satırda kaldığımızı oku
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f: f.write("0")
    
    with open(PROGRESS_FILE, "r") as f:
        try:
            mevcut_index = int(f.read().strip())
        except:
            mevcut_index = 0

    # 2. Dosyaları listeye aktar
    def dosya_listele(dosya_adi):
        with open(dosya_adi, "r", encoding="utf-8") as f:
            # Sadece dolu satırları al ve kenar boşluklarını temizle
            return [line.strip() for line in f.readlines() if line.strip()]

    tum_sozler = dosya_listele(SOZLER_DOSYASI)
    tum_basliklar = dosya_listele(BASLIKLAR_DOSYASI)
    tum_aciklamalar = dosya_listele(ACIKLAMALAR_DOSYASI)

    # 3. Sıradaki veriyi seç (Eğer liste bittiyse hata verme, en başa dön)
    if mevcut_index >= len(tum_sozler):
        mevcut_index = 0

    # Verileri paketle (Kesinlikle numara eklemiyoruz, sadece metin)
    return {
        "soz": tum_sozler[mevcut_index].upper(),
        "baslik": tum_basliklar[mevcut_index],
        "aciklama": tum_aciklamalar[mevcut_index],
        "yeni_index": mevcut_index + 1
    }

if __name__ == "__main__":
    # Veriyi çek
    data = guncel_veriyi_getir()
    print(f"🔄 Satır {data['yeni_index']} işleniyor: {data['baslik']}")

    # Video Düzenleme
    if not os.path.exists(VIDEO_DOSYASI):
        print(f"❌ HATA: {VIDEO_DOSYASI} bulunamadı!")
        exit(1)

    clip = VideoFileClip(VIDEO_DOSYASI)
    
    # Müzik varsa ekle
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)

    # Videonun üstüne sözü yaz (Numara içermez, sadece kalın söz)
    txt = TextClip(
        data['soz'], 
        fontsize=65, 
        color='white', 
        font='DejaVu-Sans-Bold', 
        method='caption', 
        size=(clip.w * 0.85, None), 
        align='center'
    ).set_duration(clip.duration).set_position('center')

    final = CompositeVideoClip([clip, txt])
    final_output = "video_upload.mp4"
    final.write_videofile(final_output, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YouTube'a Yükle
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
        
        media = MediaFileUpload(final_output, chunksize=-1, resumable=True)
        yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
        
        # Yükleme bittikten sonra sıradaki numarayı dosyaya yaz (Takip mekanizması)
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(data['yeni_index']))
            
        print(f"🚀 Başarıyla yüklendi! Bir sonraki sıra: {data['yeni_index']}")
    else:
        print("❌ token.json bulunamadı!")
        exit(1)
