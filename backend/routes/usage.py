import datetime
import json
import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from config import ELEVENLABS_API_KEY, OPENAI_API_KEY, OUTPUT_DIR, MAX_CONCURRENT_VIDEOS
from repositories.file_repository import get_folder_size, get_video_duration
from utils.resource_monitor import ResourceMonitor
from core.generator import video_generation_semaphore

usage_bp = Blueprint('usage_api', __name__, url_prefix='/api')

@usage_bp.route('/elevenlabs/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_elevenlabs_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        response = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=headers, timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Could not fetch usage data: {e}"}), 500

@usage_bp.route('/openai/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_openai_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    return jsonify({
        "status": "active",
        "current_month": datetime.datetime.now().strftime('%B %Y'),
        "note": "OpenAI balance requires special API access, assuming active."
    })

@usage_bp.route('/storage/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_storage_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    if not OUTPUT_DIR.exists():
        return jsonify({"total_size_bytes": 0, "video_count": 0, "projects": []})
    
    total_size, video_count = 0, 0
    projects, video_type_counts = [], {"standard": 0, "shorts": 0}
    
    for project_dir in OUTPUT_DIR.iterdir():
        if project_dir.is_dir():
            total_size += get_folder_size(project_dir)
            if (project_dir / "final_video.mp4").exists():
                video_count += 1
                duration = get_video_duration(project_dir / "final_video.mp4")
                video_type = "shorts" if duration and duration < 61 else "standard"
                video_type_counts[video_type] += 1
    
    return jsonify({
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024*1024), 1),
        "total_size_gb": round(total_size / (1024*1024*1024), 2),
        "video_count": video_count,
        "video_type_counts": video_type_counts,
    })

@usage_bp.route('/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"})

@usage_bp.route('/system/status', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_system_status():
    stats = ResourceMonitor.get_system_stats()
    return jsonify({
        "system": stats,
        "video_generation": {
            "active": MAX_CONCURRENT_VIDEOS - video_generation_semaphore._value,
            "max_concurrent": MAX_CONCURRENT_VIDEOS,
            "can_start_new": ResourceMonitor.can_start_new_video()
        }
    })