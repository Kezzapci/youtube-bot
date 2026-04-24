import os, random, requests, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB SİSTEM AYARI (ImageMagick Kilidini Açmak İçin)
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

def pexels_video_indir():
    print("🎬 Pexels'ten video aranıyor...")
    api_key = os.getenv("PEXELS_API_KEY")
    # Arama terimlerini çeşitlendirdik
    query = random.choice(["nature", "landscape", "mountains", "sea", "forest", "dark nature", "ocean"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": api_key}
    
    r = requests.get(url, headers=headers).json()
    # Rastgele bir video seç ve indir
    video_data = random.choice(r['videos'])
    video_url = video_data['video_files'][0]['link']
    
    print(f"📥 Video indiriliyor: {query}")
    with open("video.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    return "video.mp4"

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
    video_path = pexels_video_indir() 
    
    # Videoyu işle (İlk 10 saniye)
    clip = VideoFileClip(video_path).subclip(0, 10)
    
    # Müzik varsa ekle
    if os.path.exists("muzik.mp3"):
        music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
        clip = clip.set_audio(music)
    
    # Yazıyı ekle
    txt = TextClip(soz, fontsize=50, color='white', font='Arial-Bold', method='caption', 
                   size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    
    final = CompositeVideoClip([clip, txt])
    final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

    # YOUTUBE'A YÜKLE
    print("📤 YouTube'a gönderiliyor...")
    with open('token.json', 'rb') as t: creds = pickle.load(t)
    yt = build('youtube', 'v3', credentials=creds)

    aciklama = f"Zihnini güçlendir! 💪\n\nSöz: {soz}\n\n#motivasyon #başarı #shorts"
    body = {
        'snippet': {
            'title': f"{soz[:50]}... #shorts",
            'description': aciklama,
            'categoryId': '22'
        },
        'status': {'privacyStatus': 'public'}
    }
    
    media = MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
    yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
    print("✅ İşlem Başarılı! Video yayında.")
