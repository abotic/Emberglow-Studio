import re
import json
import time
import shutil
import gc
import threading
from pathlib import Path
from threading import Lock

from config import OUTPUT_DIR, MAX_CONCURRENT_VIDEOS
from core.models import GenerationConfig, VideoSettings, ProgressUpdate, VideoGenerationError
from services.script_service import generate_script, generate_youtube_metadata
from services.asset_service import gather_visuals
from services.audio_service import generate_voiceover
from services.render_service import render_video_simple, generate_thumbnail
from repositories.progress_repository import mark_video_completed, add_generating_video, remove_generating_video

generation_progress = {}
progress_lock = Lock()
video_generation_semaphore = threading.Semaphore(MAX_CONCURRENT_VIDEOS)


class VideoGenerator:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.project_name = self._sanitize_project_name(config.topic)
        self.project_dir = OUTPUT_DIR / self.project_name
        self.video_settings = self._get_video_settings()
        self.progress_file = self.project_dir / ".progress.json"
        self.setup_directories()

    def _sanitize_project_name(self, topic: str) -> str:
        name = re.sub(r'[^\w\s-]', '', topic.lower())
        name = re.sub(r'[-\s]+', '_', name)
        name = name[:100]
        return name.strip('_')

    def setup_directories(self):
        try:
            self.project_dir.mkdir(parents=True, exist_ok=True)
            (self.project_dir / "assets").mkdir(exist_ok=True)
            (self.project_dir / "audio").mkdir(exist_ok=True)
        except Exception as e:
            raise VideoGenerationError(f"Failed to setup directories: {e}")

    def _get_video_settings(self) -> VideoSettings:
        if self.config.video_type == "shorts":
            return VideoSettings(
                clip_duration=6.0,
                word_count_min=80,
                word_count_max=100,
                tts_model="eleven_monolingual_v1"
            )
        else:
            return VideoSettings(
                clip_duration=14.0,
                word_count_min=800,
                word_count_max=1000,
                tts_model="eleven_monolingual_v1"
            )

    def update_progress(self, update: ProgressUpdate):
        progress_data = {
            "step": update.step,
            "percentage": update.percentage,
            "status": update.status,
            "topic": self.config.topic,
            "video_type": self.config.video_type,
            "details": update.details,
            "progress_id": self.config.progress_id
        }
        
        with progress_lock:
            generation_progress[self.config.progress_id] = progress_data
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f)
        except:
            pass

    def _cleanup_on_error(self):
        try:
            print(f"🧹 Cleaning up after error for project: {self.project_name}")
            remove_generating_video(self.project_name)
            if self.project_dir.exists():
                shutil.rmtree(self.project_dir, ignore_errors=True)
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def _cleanup_on_success(self):
        try:
            print(f"🧹 Cleaning up temporary files...")
            
            audio_parts_dir = self.project_dir / "audio" / "parts"
            if audio_parts_dir.exists():
                shutil.rmtree(audio_parts_dir, ignore_errors=True)
            
            for pattern in ['temp-audio-*.m4a', '*.tmp']:
                for temp_file in self.project_dir.rglob(pattern):
                    try:
                        temp_file.unlink()
                    except:
                        pass
            
            gc.collect()
        except Exception as e:
            print(f"Error during post-success cleanup: {e}")

    def generate(self):
        video_generation_semaphore.acquire()
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            add_generating_video(self.project_name, self.config.topic, self.config.progress_id, self.config.video_type)
            
            self.update_progress(ProgressUpdate(step="Generating script", percentage=10, details="Creating engaging narrative..."))
            script = generate_script(self.config.video_type, self.config.category, self.config.topic, self.video_settings)
            
            if not script or len(script) < 50:
                raise VideoGenerationError("Generated script is too short or empty")
            
            self.update_progress(ProgressUpdate(step="Generating voiceover", percentage=25, details="Creating professional narration..."))
            audio_path = generate_voiceover(script, self.project_dir, self.config.video_type, self.config.voice_id, self.video_settings.tts_model)
            
            if not audio_path or not Path(audio_path).exists():
                raise VideoGenerationError("Audio generation failed")

            self.update_progress(ProgressUpdate(step="Gathering visuals", percentage=40, details="Finding perfect visuals..."))
            assets = gather_visuals(self.config.generation_mode, self.config.video_type, self.config.category, script, self.config.topic, self.project_dir, audio_path, self.video_settings, self.config.ai_provider, self.config.style_preset)
            
            if not assets:
                raise VideoGenerationError("No assets were found or generated")

            self.update_progress(ProgressUpdate(step="Rendering video", percentage=80, details="This can take several minutes..."))
            video_path = render_video_simple(assets, audio_path, self.project_dir, self.video_settings)
            
            if not video_path or not Path(video_path).exists():
                raise VideoGenerationError("Video rendering failed")
            
            self.update_progress(ProgressUpdate(step="Generating thumbnail", percentage=95, details="Creating eye-catching thumbnail..."))
            generate_thumbnail(assets=assets, topic=self.config.topic, script=script, project_dir=self.project_dir, generation_mode=self.config.generation_mode, ai_provider=self.config.ai_provider, style_preset=self.config.style_preset)
            
            self.update_progress(ProgressUpdate(step="Generating metadata", percentage=98, details="Creating YouTube metadata..."))
            metadata = generate_youtube_metadata(self.config.topic, script, self.config.video_type)
            metadata['original_topic'] = self.config.topic

            metadata_path = self.project_dir / "youtube_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            success = True

        except VideoGenerationError as e:
            error_msg = str(e)
            print(f"Generation failed: {error_msg}")
            
        except Exception as e:
            error_msg = str(e) if str(e) else type(e).__name__
            print(f"Unexpected error: {error_msg}")
            
        finally:
            duration = time.time() - start_time
            
            if success:
                try:
                    mark_video_completed(self.config.topic)
                    self.update_progress(ProgressUpdate(step="Complete", percentage=100, status="completed", details=f"Generated in {duration:.1f}s"))
                    
                    time.sleep(5)
                    
                    self._cleanup_on_success()
                    remove_generating_video(self.project_name)
                    
                    with progress_lock:
                        if self.config.progress_id in generation_progress:
                            del generation_progress[self.config.progress_id]
                    
                    if self.progress_file.exists():
                        try:
                            self.progress_file.unlink()
                        except:
                            pass
                    
                    print(f"Complete! (Took {duration:.2f} seconds)")
                    
                except Exception as e:
                    print(f"Post-generation error (video still saved): {e}")
                    remove_generating_video(self.project_name)
                    self.update_progress(ProgressUpdate(step="Complete", percentage=100, status="completed"))
            else:
                self._cleanup_on_error()
                self.update_progress(ProgressUpdate(step="Error", percentage=0, status="error", details=error_msg or "Unknown error occurred"))
            
            video_generation_semaphore.release()
            gc.collect()


def get_progress(progress_id: str) -> dict:
    with progress_lock:
        if progress_id in generation_progress:
            return generation_progress[progress_id]
    
    for project_dir in OUTPUT_DIR.iterdir():
        if project_dir.is_dir():
            progress_file = project_dir / ".progress.json"
            if progress_file.exists():
                try:
                    with open(progress_file, 'r') as f:
                        data = json.load(f)
                        if data and data.get('progress_id') == progress_id:
                            with progress_lock:
                                generation_progress[progress_id] = data
                            return data
                except:
                    pass
    
    return {
        "step": "Waiting",
        "percentage": 0,
        "status": "waiting",
        "details": None
    }