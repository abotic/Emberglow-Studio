import time
import requests
import random
from pathlib import Path
from typing import Optional
import re

from config import STABILITY_API_KEY, RETRY_ATTEMPTS

def generate_stability_image(prompt: str, index: int, project_dir: Path, style_preset: str) -> Optional[str]:
    if not STABILITY_API_KEY:
        return None

    endpoint = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    headers = {"authorization": f"Bearer {STABILITY_API_KEY}", "accept": "image/*"}
    data = {
        "prompt": prompt,
        "negative_prompt": "text, letters, watermark, signature, numbers, blurry, low quality",
        "aspect_ratio": "16:9",
        "model": "sd3.5-large",
        "style_preset": style_preset,
        "output_format": "png",
        "seed": 0
    }

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(endpoint, headers=headers, files={"none": ''}, data=data, timeout=45)
            response.raise_for_status()
            
            filename = f"sd35_large_turbo_{index}_{random.randint(1000, 9999)}.png"
            filepath = project_dir / "assets" / filename
            filepath.write_bytes(response.content)
            return str(filepath)
        except Exception as e:
            if attempt == RETRY_ATTEMPTS - 1:
                print(f"SD 3.5 Large Turbo failed for index {index}: {e}")
                return None
            time.sleep(2 * (attempt + 1))
    
    return None

def generate_ai_thumbnail_image(topic: str, script: str, project_dir: Path, style_preset: str) -> Optional[str]:
    if not STABILITY_API_KEY:
        return None

    flag_instruction = ""
    country_match = re.search(r'think about ([\w\s]+)\?$', topic, re.IGNORECASE)
    if country_match:
        country_name = country_match.group(1).title()
        flag_instruction = f"The image MUST prominently feature the national flag of {country_name}."

    prompt = f"""
    Create a hyper-realistic, 16:9 thumbnail image for a YouTube video about "{topic}".
    The image should be visually stunning, intriguing, and emotionally evocative, with a single, clear focal point.
    Focus on the core concept from this script excerpt: "{script[:250]}".
    {flag_instruction}
    CRITICAL: The image must contain absolutely no text, letters, logos, or watermarks.
    Style: {style_preset}, dramatic lighting, professional photography, ultra-detailed.
    """

    endpoint = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    headers = {"authorization": f"Bearer {STABILITY_API_KEY}", "accept": "image/*"}
    data = {
        "prompt": prompt,
        "negative_prompt": "text, letters, words, logo, watermark, signature, numbers, blurry, cartoon, amateur, ugly, deformed",
        "aspect_ratio": "16:9",
        "style_preset": style_preset,
        "output_format": "jpeg",
        "seed": 0
    }

    for attempt in range(RETRY_ATTEMPTS):
        try:
            if attempt > 0:
                time.sleep(5 * attempt)
            
            response = requests.post(endpoint, headers=headers, files={"none": ''}, data=data, timeout=60)
            response.raise_for_status()
            
            filepath = project_dir / "thumbnail.jpg"
            filepath.write_bytes(response.content)
            return str(filepath)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 404] and attempt < RETRY_ATTEMPTS - 1:
                continue
            return None
        except Exception:
            if attempt == RETRY_ATTEMPTS - 1:
                return None
    
    return None