import os
from elevenlabs import set_api_key as set_elevenlabs_key
from dotenv import load_dotenv
from pathlib import Path
import platform

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

INTRO_CLIPS_COUNT = 4
INTRO_CLIP_DURATION = 7.0
MAX_IMAGE_WORKERS = 8
MAX_DOWNLOAD_WORKERS = 8
RETRY_ATTEMPTS = 3
IMAGE_BUFFER_COUNT = 3

SCRIPT_CHUNK_LIMIT = 9500
MAX_SCRIPT_RETRIES = 3

IS_MAC = platform.processor() == 'arm' and platform.system() == 'Darwin'
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT', 'false').lower() == 'true'

if IS_MAC:
    MAX_CONCURRENT_VIDEOS = 4
    VIDEO_ENCODING_THREADS = 8
    ENCODING_PRESET = 'fast'
elif IS_RAILWAY:
    MAX_CONCURRENT_VIDEOS = 8
    VIDEO_ENCODING_THREADS = 8
    ENCODING_PRESET = 'ultrafast'
else:
    MAX_CONCURRENT_VIDEOS = 8
    VIDEO_ENCODING_THREADS = 8
    ENCODING_PRESET = 'fast'

CACHE_DIR = Path(os.getenv('CACHE_DIR', 'cache'))
CACHE_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("youtube_videos")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = DATA_DIR / "progress.json"
GENERATING_VIDEOS_FILE = DATA_DIR / "generating_videos.json"

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5002').split(',')

class ConfigurationError(Exception):
    pass

def validate_config():
    required = {
        'OPENAI_API_KEY': OPENAI_API_KEY,
        'ELEVENLABS_API_KEY': ELEVENLABS_API_KEY,
        'PEXELS_API_KEY': PEXELS_API_KEY,
        'STABILITY_API_KEY': STABILITY_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ConfigurationError(f"Missing required API keys: {', '.join(missing)}")

def initialize_apis():
    validate_config()
    
    set_elevenlabs_key(ELEVENLABS_API_KEY)