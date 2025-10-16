import os
import gc
import random
from pathlib import Path
from typing import List
from contextlib import contextmanager

from moviepy import AudioFileClip, CompositeVideoClip, VideoFileClip, ImageClip
from PIL import Image

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, VIDEO_ENCODING_THREADS, 
    ENCODING_PRESET, INTRO_CLIPS_COUNT, INTRO_CLIP_DURATION
)
from core.models import VideoSettings, RenderError
from services.stability_service import generate_ai_thumbnail_image
from services.asset_service import create_fallback_image


@contextmanager
def managed_clip(clip):
    try:
        yield clip
    finally:
        try:
            if hasattr(clip, 'close'):
                clip.close()
            if hasattr(clip, 'reader') and clip.reader:
                try:
                    clip.reader.close()
                except:
                    pass
        except Exception as e:
            print(f"Warning: Error closing clip: {e}")


@contextmanager
def managed_image(image):
    try:
        yield image
    finally:
        try:
            if image and hasattr(image, 'close'):
                image.close()
        except Exception as e:
            print(f"Warning: Error closing image: {e}")


def render_video_simple(assets: List[str], audio_path: str, project_dir: Path, video_settings: VideoSettings) -> str:
    print("🎬 Rendering video with variable intro pacing...")
    clips = []
    opened_resources = []
    audio = None
    
    try:
        audio = AudioFileClip(audio_path)
        opened_resources.append(audio)
        total_duration = audio.duration
        print(f"Target duration: {total_duration:.1f}s")

        valid_assets = sorted(
            [a for a in assets if a and os.path.exists(a)],
            key=lambda p: _extract_index_from_filename(p)
        )

        if not valid_assets:
            print("No valid assets found! Using fallbacks.")
            valid_assets = [create_fallback_image(i, project_dir) for i in range(10)]
        
        video_assets = [a for a in valid_assets if a.lower().endswith(('.mp4', '.mov', '.avi'))]
        image_assets = [a for a in valid_assets if a.lower().endswith(('.png', '.jpg', '.jpeg'))]
        asset_sequence = video_assets + image_assets

        current_time = 0.0
        clip_number = 0
        
        while current_time < total_duration and asset_sequence:
            if clip_number < INTRO_CLIPS_COUNT:
                target_duration = INTRO_CLIP_DURATION
            else:
                target_duration = video_settings.clip_duration
            
            clip_duration = min(target_duration, total_duration - current_time)
            asset_path = asset_sequence[clip_number % len(asset_sequence)]
            
            clip = None
            try:
                if asset_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    clip = VideoFileClip(asset_path)
                    opened_resources.append(clip)
                    
                    if clip.duration > clip_duration:
                        start = random.uniform(0, max(0, clip.duration - clip_duration))
                        clip = clip.subclipped(start, min(start + clip_duration, clip.duration))
                    elif clip.duration < clip_duration:
                        try:
                            clip = clip.looped(duration=clip_duration)
                        except AttributeError:
                            times_to_loop = int(clip_duration / clip.duration) + 1
                            from moviepy import concatenate_videoclips
                            clip = concatenate_videoclips([clip] * times_to_loop).subclipped(0, clip_duration)
                else:
                    clip = ImageClip(asset_path).with_duration(clip_duration)
                
                target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
                clip_ratio = clip.w / clip.h

                if clip_ratio > target_ratio:
                    resized_clip = clip.resized(height=VIDEO_HEIGHT)
                else:
                    resized_clip = clip.resized(width=VIDEO_WIDTH)

                final_clip = resized_clip.cropped(
                    x_center=resized_clip.w / 2,
                    y_center=resized_clip.h / 2,
                    width=VIDEO_WIDTH,
                    height=VIDEO_HEIGHT
                )
                
                clips.append(final_clip.with_start(current_time))
                current_time += clip_duration
                clip_number += 1

            except Exception as e:
                print(f"Skipping broken asset {os.path.basename(asset_path)}: {e}")
                if clip and hasattr(clip, 'close'):
                    try:
                        clip.close()
                    except:
                        pass
                clip_number += 1
                continue
        
        if not clips:
            raise RenderError("No valid clips could be processed")

        video = CompositeVideoClip(
            clips, 
            size=(VIDEO_WIDTH, VIDEO_HEIGHT)
        ).with_duration(total_duration).with_audio(audio)
        
        opened_resources.append(video)
        
        output_path = project_dir / "final_video.mp4"
        temp_audio_path = project_dir / "audio" / f"temp-audio-{random.randint(1000,9999)}.m4a"
        
        video.write_videofile(
            str(output_path),
            fps=FPS,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(temp_audio_path),
            threads=VIDEO_ENCODING_THREADS,
            preset=ENCODING_PRESET,
            logger=None
        )
        
        print(f"Video rendered successfully: {output_path}")
        return str(output_path)
        
    except RenderError:
        raise
    except Exception as e:
        raise RenderError(f"Video rendering failed: {e}")
    finally:
        print("Cleaning up video resources...")
        for resource in opened_resources:
            try:
                if hasattr(resource, 'close'):
                    resource.close()
            except Exception as e:
                print(f"Warning: Error closing resource: {e}")
        
        for clip in clips:
            try:
                if hasattr(clip, 'close'):
                    clip.close()
            except:
                pass
        
        clips.clear()
        opened_resources.clear()
        gc.collect()


def generate_thumbnail(
    assets: List[str], 
    topic: str, 
    script: str, 
    project_dir: Path, 
    generation_mode: str, 
    ai_provider: str, 
    style_preset: str
) -> str:
    thumbnail_dest_path = project_dir / "thumbnail.jpg"
    base_image = None

    if generation_mode != 'stock' and ai_provider == 'stability':
        ai_thumb_path = generate_ai_thumbnail_image(topic, script, project_dir, style_preset)
        if ai_thumb_path:
            print(f"AI Thumbnail generation successful")
            return ai_thumb_path
        print("AI thumbnail generation failed. Falling back to using a project asset.")

    print("Selecting best asset for thumbnail...")
    final_video_path = project_dir / "final_video.mp4"
    
    if final_video_path.exists():
        video_clip = None
        try:
            with managed_clip(VideoFileClip(str(final_video_path))) as video_clip:
                frame_time = min(video_clip.duration * 0.25, video_clip.duration - 0.1)
                if frame_time > 0:
                    frame = video_clip.get_frame(frame_time)
                    with managed_image(Image.fromarray(frame)) as base_image:
                        base_image = base_image.resize((1280, 720), Image.Resampling.LANCZOS).convert("RGB")
                        base_image.save(thumbnail_dest_path, "JPEG", quality=90, optimize=True)
                        print(f"Thumbnail created from video frame")
                        return str(thumbnail_dest_path)
        except Exception as e:
            print(f"Could not extract frame from video: {e}")
        finally:
            if video_clip:
                try:
                    video_clip.close()
                except:
                    pass

    image_assets = [a for a in assets if a and a.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if image_assets:
        selected_asset = random.choice(image_assets)
        try:
            with managed_image(Image.open(selected_asset)) as img:
                img = img.resize((1280, 720), Image.Resampling.LANCZOS).convert("RGB")
                img.save(thumbnail_dest_path, "JPEG", quality=90, optimize=True)
                print(f"Thumbnail created from image asset")
                return str(thumbnail_dest_path)
        except Exception as e:
            print(f"Could not open asset image: {e}")

    print("Creating fallback thumbnail...")
    fallback_path = create_fallback_image(0, project_dir)
    
    try:
        with managed_image(Image.open(fallback_path)) as img:
            img = img.resize((1280, 720), Image.Resampling.LANCZOS).convert("RGB")
            img.save(thumbnail_dest_path, "JPEG", quality=90, optimize=True)
    except Exception as e:
        print(f"Error creating fallback thumbnail: {e}")
        import shutil
        shutil.copy(fallback_path, thumbnail_dest_path)
    
    print(f"Fallback thumbnail saved")
    return str(thumbnail_dest_path)


def _extract_index_from_filename(filepath: str) -> int:
    basename = os.path.basename(filepath)
    parts = basename.split('_')
    for part in parts:
        if part.isdigit():
            return int(part)
    return 0