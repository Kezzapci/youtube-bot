from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"

SOZLER_FILE = DATA_DIR / "rusca_sozler.txt"
BASLIKLAR_FILE = DATA_DIR / "youtube_basliklari.txt"
ACIKLAMALAR_FILE = DATA_DIR / "youtube_aciklamalari.txt"

BACKGROUND_VIDEO = ASSETS_DIR / "background.mp4"
MUSIC_FILE = ASSETS_DIR / "music.mp3"

STATE_FILE = BASE_DIR / "state.json"
OUTPUT_VIDEO = OUTPUT_DIR / "yukle.mp4"

CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"

YOUTUBE_CATEGORY_ID = os.getenv("YOUTUBE_CATEGORY_ID", "27")
YOUTUBE_PRIVACY = os.getenv("YOUTUBE_PRIVACY", "public")  # public, unlisted, private
YOUTUBE_LANGUAGE = os.getenv("YOUTUBE_LANGUAGE", "ru")

FONT_SIZE = int(os.getenv("FONT_SIZE", "64"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.30"))
