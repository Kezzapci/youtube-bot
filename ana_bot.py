import os, pickle
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GİTHUB SİSTEM AYARI
IMAGEMAGICK_EXE = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})

def siradaki_sozu_al():
    prog_file = "siradaki_soz.txt"
    if not os.path.exists(prog_file):
        with open(prog_file, "w") as f: f.write("0")
    with open(prog_file, "r") as f:
        index = int(f.read().strip() or 0)
    with open("motivasyon_sozleri_1000.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    if index >= len(lines): index = 0
    soz = lines[index].strip()
    with open(prog_file, "w") as f: f.write(str(index + 1))
    return soz.upper()

if __name__ == "__main__":
    soz = siradaki_sozu_al()
    clip = VideoFileClip("video.mp4")
    music = AudioFileClip("muzik.mp3").subclip(0, clip.duration).volumex(0.3)
    txt = TextClip(soz, fontsize=70, color='white', font='Arial-Bold', method='caption', size=(clip.w*0.8, None), align='center').set_duration(clip.duration).set_position('center')
    final = CompositeVideoClip([clip, txt]).set_audio(music)
    final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

    with open('token.json', 'rb') as t: creds = pickle.load(t)
    yt = build('youtube', 'v3', credentials=creds)
    body = {'snippet': {'title': f"{soz[:50]}... #shorts", 'categoryId': '22'}, 'status': {'privacyStatus': 'public'}}
    media = MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
    yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
    print("🚀 Video Atıldı!")
