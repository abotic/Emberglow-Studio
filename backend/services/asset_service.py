import math
import random
import concurrent.futures
from pathlib import Path
from typing import List, Optional

from moviepy import AudioFileClip
from PIL import Image, ImageDraw

from config import IMAGE_BUFFER_COUNT, INTRO_CLIPS_COUNT, INTRO_CLIP_DURATION, MAX_IMAGE_WORKERS
from core.models import VideoSettings, AssetGenerationError
from services.stability_service import generate_stability_image
from services.stock_service import search_pexels, download_assets_parallel
from utils.stock_search import generate_smart_keywords

def gather_visuals(
    generation_mode: str, video_type: str, category: str, script: str, topic: str,
    project_dir: Path, audio_path: str, video_settings: VideoSettings,
    ai_provider: str, style_preset: str
) -> List[str]:
    if generation_mode == 'stability':
        images_needed = _calculate_images_needed(audio_path, video_settings)
        return _generate_stability_parallel(script, topic, images_needed, project_dir, style_preset)
    
    return _gather_stock_visuals(script, topic, audio_path, video_settings, project_dir)

def _generate_stability_parallel(script: str, topic: str, images_needed: int, project_dir: Path, style_preset: str) -> List[str]:
    print(f"Generating {images_needed} SD 3.5 Large Turbo images in parallel...")
    paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
    if not paragraphs: 
        paragraphs = [script]
    
    tasks = []
    for i in range(images_needed):
        paragraph = paragraphs[i % len(paragraphs)]
        prompt = f"Educational illustration of '{topic}' related to '{paragraph[:100]}'. Cinematic, high detail, photorealistic."
        tasks.append((prompt, i, project_dir, style_preset))
        
    assets = _execute_parallel_generation(tasks, project_dir)
    print(f"Generated {len(assets)} images using SD 3.5 Large Turbo.")
    return assets

def _execute_parallel_generation(tasks: List[tuple], project_dir: Path) -> List[str]:
    assets = [None] * len(tasks)
    tasks_map = {i: task for i, task in enumerate(tasks)}

    for attempt in range(3):
        if not tasks_map:
            break
        
        print(f"--- Generation Attempt #{attempt + 1} for {len(tasks_map)} images ---")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_IMAGE_WORKERS) as executor:
            future_to_index = {}
            for index, task in tasks_map.items():
                future = executor.submit(generate_stability_image, *task)
                future_to_index[future] = index

            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                asset_path = future.result()
                
                if asset_path:
                    assets[index] = asset_path
                    if index in tasks_map:
                        del tasks_map[index]

        if tasks_map and attempt < 2:
            print(f"{len(tasks_map)} tasks failed. Retrying...")
            
    for index in tasks_map.keys():
        assets[index] = create_fallback_image(index, project_dir)
        
    return [asset for asset in assets if asset]

def _gather_stock_visuals(script: str, topic: str, audio_path: str, video_settings: VideoSettings, project_dir: Path) -> List[str]:
    images_needed = _calculate_images_needed(audio_path, video_settings)
    num_keywords = 7
    assets_per_keyword = math.ceil((images_needed + 5) / num_keywords)
    
    print(f"Needing ~{images_needed} clips. Searching for {assets_per_keyword} assets from top {num_keywords} keywords.")
    
    keywords = generate_smart_keywords(topic, script)
    all_assets = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_keywords) as executor:
        future_to_search = {
            executor.submit(search_pexels, keyword, assets_per_keyword): keyword 
            for keyword in keywords[:num_keywords]
        }
        for future in concurrent.futures.as_completed(future_to_search):
            try:
                all_assets.extend(future.result())
            except Exception as exc:
                print(f"Search for '{future_to_search[future]}' failed: {exc}")

    unique_ids = set()
    unique_assets = [asset for asset in all_assets if asset['id'] not in unique_ids and not unique_ids.add(asset['id'])]
    
    return download_assets_parallel(unique_assets, project_dir)

def _calculate_images_needed(audio_path: str, video_settings: VideoSettings) -> int:
    audio_duration = 30
    if Path(audio_path).exists():
        try:
            with AudioFileClip(str(audio_path)) as audio:
                audio_duration = audio.duration
        except Exception:
            pass

    intro_total_seconds = INTRO_CLIPS_COUNT * INTRO_CLIP_DURATION

    if audio_duration <= intro_total_seconds:
        images_needed = math.ceil(audio_duration / INTRO_CLIP_DURATION)
    else:
        main_section_duration = audio_duration - intro_total_seconds
        main_clips_needed = math.ceil(main_section_duration / video_settings.clip_duration)
        images_needed = INTRO_CLIPS_COUNT + main_clips_needed
    
    return images_needed + IMAGE_BUFFER_COUNT

def create_fallback_image(index: int, project_dir: Path) -> str:
    img = Image.new('RGB', (1920, 1080))
    draw = ImageDraw.Draw(img)
    colors = [((20, 20, 50), (50, 50, 100)), ((50, 20, 20), (100, 50, 50)), ((20, 50, 20), (50, 100, 50))]
    start_color, end_color = colors[index % len(colors)]
    for y in range(1080):
        ratio = y / 1080
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.rectangle([(0, y), (1920, y + 1)], fill=(r, g, b))
    
    filename = f"fallback_{index}_{random.randint(1000, 9999)}.jpg"
    filepath = project_dir / "assets" / filename
    img.save(filepath, quality=90)
    return str(filepath)