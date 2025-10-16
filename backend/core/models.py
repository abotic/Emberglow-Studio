from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class GenerationConfig:
    topic: str
    category: str
    progress_id: str
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    generation_mode: str = "stock"
    video_type: str = "standard"
    ai_provider: str = "stability"
    style_preset: str = "cinematic"

@dataclass
class VideoSettings:
    clip_duration: float
    word_count_min: int
    word_count_max: int
    tts_model: str

@dataclass
class ProgressUpdate:
    step: str
    percentage: int
    status: str = "processing"
    details: Optional[str] = None

class VideoGenerationError(Exception):
    pass

class ScriptGenerationError(VideoGenerationError):
    pass

class AssetGenerationError(VideoGenerationError):
    pass

class AudioGenerationError(VideoGenerationError):
    pass

class RenderError(VideoGenerationError):
    pass