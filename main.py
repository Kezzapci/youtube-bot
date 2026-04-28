import json
from pathlib import Path
from typing import List, Dict, Any

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


BASE_DIR = Path(__file__).resolve().parent

SOZLER_FILE = BASE_DIR / "data" / "sozler.txt"
BASLIKLAR_FILE = BASE_DIR / "data" / "youtube_basliklari.txt"
ACIKLAMALAR_FILE = BASE_DIR / "data" / "youtube_aciklamalari.txt"

BACKGROUND_VIDEO = BASE_DIR / "assets" / "Wolf_Motivation_Video_y9oxsx15.mp4"
MUSIC_FILE = BASE_DIR / "assets" / "music.mp3"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_VIDEO = OUTPUT_DIR / "final_video.mp4"

TOKEN_FILE = BASE_DIR / "token.json"
STATE_FILE = BASE_DIR / "state.json"

YOUTUBE_CATEGORY_ID = "22"
YOUTUBE_PRIVACY = "public"
YOUTUBE_LANGUAGE = "ru"

FONT_SIZE = 72
VIDEO_FPS = 30
MUSIC_VOLUME = 0.35

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def read_lines(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {path}")

    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"index": 0}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"index": 0}


def save_state(index: int) -> None:
    STATE_FILE.write_text(
        json.dumps({"index": index}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_next_data() -> Dict[str, Any]:
    sozler = read_lines(SOZLER_FILE)
    basliklar = read_lines(BASLIKLAR_FILE)
    aciklamalar = read_lines(ACIKLAMALAR_FILE)

    state = load_state()
    index = int(state.get("index", 0))

    if index >= len(sozler):
        index = 0

    return {
        "index": index,
        "next_index": index + 1,
        "soz": sozler[index],
        "title": basliklar[index] if index < len(basliklar) else sozler[index][:90],
        "description": aciklamalar[index] if index < len(aciklamalar) else "",
    }


def find_font(size: int):
    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]

    for f in fonts:
        if Path(f).exists():
            return ImageFont.truetype(f, size=size)

    return ImageFont.load_default()


def wrap_text(text: str, font, max_width: int) -> str:
    words = text.split()
    lines = []
    current = ""

    img = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(img)

    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)


def create_text_overlay(text: str, width: int, height: int) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    overlay_path = OUTPUT_DIR / "text_overlay.png"

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = find_font(FONT_SIZE)
    wrapped = wrap_text(text.upper(), font, int(width * 0.82))

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font,
        spacing=18,
        align="center",
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) / 2
    y = (height - text_h) / 2

    draw.multiline_text(
        (x + 5, y + 5),
        wrapped,
        font=font,
        fill=(0, 0, 0, 200),
        spacing=18,
        align="center",
    )

    draw.multiline_text(
        (x, y),
        wrapped,
        font=font,
        fill=(255, 255, 255, 255),
        spacing=18,
        align="center",
    )

    img.save(overlay_path)
    return overlay_path


def render_video(text: str) -> Path:
    if not BACKGROUND_VIDEO.exists():
        raise FileNotFoundError(f"Video bulunamadı: {BACKGROUND_VIDEO}")

    OUTPUT_DIR.mkdir(exist_ok=True)

    clip = VideoFileClip(str(BACKGROUND_VIDEO))

    if MUSIC_FILE.exists():
        music = AudioFileClip(str(MUSIC_FILE))
        music = music.subclip(0, min(clip.duration, music.duration))
        music = music.volumex(MUSIC_VOLUME)
        clip = clip.set_audio(music)

    overlay = create_text_overlay(text, clip.w, clip.h)

    text_clip = (
        ImageClip(str(overlay))
        .set_duration(clip.duration)
        .set_position("center")
    )

    final = CompositeVideoClip([clip, text_clip])

    final.write_videofile(
        str(OUTPUT_VIDEO),
        codec="libx264",
        audio_codec="aac",
        fps=VIDEO_FPS,
        preset="medium",
        threads=2,
    )

    clip.close()
    final.close()

    return OUTPUT_VIDEO


def get_youtube_service():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("token.json bulunamadı.")

    credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not credentials.valid:
        raise RuntimeError("token.json geçersiz. Yeniden token alman lazım.")

    return build("youtube", "v3", credentials=credentials)


def upload_video(video_path: Path, title: str, description: str) -> str:
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": YOUTUBE_CATEGORY_ID,
            "defaultLanguage": YOUTUBE_LANGUAGE,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = request.execute()
    return response.get("id", "")


def main():
    data = get_next_data()

    print(f"{data['index'] + 1}. söz hazırlanıyor...")
    print("Söz:", data["soz"])
    print("Başlık:", data["title"])

    video_path = render_video(data["soz"])

    print("YouTube'a yükleniyor...")
    video_id = upload_video(video_path, data["title"], data["description"])

    save_state(data["next_index"])

    print("Bitti.")
    print("Video ID:", video_id)


if __name__ == "__main__":
    main()
