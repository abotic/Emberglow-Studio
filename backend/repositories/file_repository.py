import os
import shutil
import json
from pathlib import Path
from moviepy import VideoFileClip
from config import OUTPUT_DIR

def get_folder_size(folder_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath) and not os.path.islink(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        print(f"Error calculating folder size for {folder_path}: {e}")
    return total_size

def get_video_duration(video_path):
    try:
        with VideoFileClip(str(video_path)) as clip:
            return clip.duration
    except Exception:
        return None

def delete_video_project(project_name):
    project_dir = OUTPUT_DIR / project_name
    if project_dir.exists():
        shutil.rmtree(project_dir)
        return True
    return False

def get_project_metadata(project_name: str) -> dict:
    metadata_path = OUTPUT_DIR / project_name / "youtube_metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading metadata for {project_name}: {e}")
    return {}