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
    
    video_path = "video.mp4" 
    
    if not os.path.exists(video_path):
        print("❌ HATA: video.mp4 dosyası bulunamadı!")
        exit()

    clip = VideoFileClip(video_path)
    
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)
    
    txt = TextClip(soz, fontsize=50, color='white', font='Arial-Bold', method='caption', 
                   size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    
    final = CompositeVideoClip([clip, txt])
    final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YOUTUBE YÜKLEME - İSPANYOLCA KEŞFET ODAKLI DÜZENLEME
    with open('token.json', 'rb') as t: 
        creds = pickle.load(t)
    yt = build('youtube', 'v3', credentials=creds)

    # İSPANYOLCA KEŞFET AYARLARI
    baslik = f"MOTIVACIÓN DIARIA: {soz[:40]}... 🔥 #shorts"
    
    aciklama = (
        f"{soz}\n\n"
        "¡Lleva tu mente un paso más allá cada día! 💪✨\n\n"
        "¿Cuál es tu secreto para el éxito? ¡Cuéntanos en los comentarios! 👇\n\n"
        "¡Suscríbete para recibir tu dosis diaria de motivación! 🚀\n\n"
        "#motivacion #exito #disciplina #desarrollopersonal #psicologia #mentalidad #shorts #reels"
    )

    body = {
        'snippet': {
            'title': baslik, 
            'description': aciklama, 
            'categoryId': '27', # Eğitim kategorisi keşfeti destekler
            'defaultLanguage': 'es' # İspanyolca olarak ayarlandı
        },
        'status': {'privacyStatus': 'public'}
    }
    
    media = MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
    yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
    print(f"🚀 Video de Motivación en Español Publicado: {baslik}")
