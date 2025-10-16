from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
import json
import time
from pathlib import Path

from config import OUTPUT_DIR
from repositories.progress_repository import (
    load_progress, save_progress, load_generating_videos, remove_generating_video
)
from repositories.file_repository import get_video_duration, delete_video_project
from utils.validation import InputValidator, ValidationError

video_bp = Blueprint('video', __name__, url_prefix='/api')


def validate_video_name(video_name: str) -> str:
    if not video_name:
        raise ValidationError("Video name is required")
    return InputValidator.sanitize_project_name(video_name)


@video_bp.route('/videos', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_videos():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    videos = []
    generating_videos = load_generating_videos()
    
    if not OUTPUT_DIR.exists():
        return jsonify([])
    
    for project_dir in OUTPUT_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        
        video_file = project_dir / "final_video.mp4"
        progress_file = project_dir / ".progress.json"
        metadata_file = project_dir / "youtube_metadata.json"
        
        if video_file.exists() and metadata_file.exists():
            thumbnail_file = project_dir / "thumbnail.jpg"
            
            file_size = video_file.stat().st_size / (1024 * 1024)
            duration = get_video_duration(video_file)
            has_metadata = metadata_file.exists()
            
            video_type = "standard"
            if duration and duration < 61:
                video_type = "shorts"
            elif metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        if metadata.get("video_type") == "shorts":
                            video_type = "shorts"
                except:
                    pass
            
            if project_dir.name in generating_videos:
                remove_generating_video(project_dir.name)
            
            videos.append({
                "name": project_dir.name,
                "display_name": project_dir.name.replace('_', ' ').title(),
                "video": f"/videos/{project_dir.name}/final_video.mp4",
                "thumbnail": f"/videos/{project_dir.name}/thumbnail.jpg" if thumbnail_file.exists() else None,
                "size_mb": round(file_size, 1),
                "duration": duration,
                "duration_formatted": f"{int(duration//60)}:{int(duration%60):02d}" if duration else None,
                "created": int(project_dir.stat().st_ctime),
                "status": "completed",
                "has_metadata": has_metadata,
                "video_type": video_type
            })
        elif progress_file.exists():
            gen_data = generating_videos.get(project_dir.name, {})
            
            videos.append({
                "name": project_dir.name,
                "display_name": gen_data.get("topic", project_dir.name.replace('_', ' ').title()),
                "video": None,
                "thumbnail": None,
                "size_mb": 0,
                "duration": None,
                "duration_formatted": None,
                "created": int(project_dir.stat().st_ctime),
                "status": "generating",
                "has_metadata": False,
                "progress_id": gen_data.get("progress_id"),
                "video_type": gen_data.get("video_type", "standard")
            })
    
    videos.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(videos)


@video_bp.route('/videos/<video_name>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
def delete_video(video_name):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        video_name = validate_video_name(video_name)
        
        progress = load_progress()
        completed = progress.get("completed", [])
        
        topic_variations = [
            video_name.replace('_', ' ').title(),
            video_name.replace('_', ' '),
            video_name
        ]
        
        for variant in topic_variations:
            if variant in completed:
                completed.remove(variant)
        
        progress["completed"] = completed
        save_progress(progress)
        
        remove_generating_video(video_name)
        
        if delete_video_project(video_name):
            return jsonify({"message": "Video deleted successfully"})
        else:
            return jsonify({"error": "Video not found"}), 404
            
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error deleting video: {e}")
        return jsonify({"error": "Failed to delete video"}), 500


@video_bp.route('/download/video/<video_name>', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_video(video_name):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        video_name = validate_video_name(video_name)
        
        project_dir = OUTPUT_DIR / video_name
        video_path = project_dir / "final_video.mp4"
        
        if not video_path.exists():
            return jsonify({"error": "Video not found"}), 404

        download_filename = f"{video_name}.mp4"
        metadata_path = project_dir / "youtube_metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                original_topic = metadata.get('original_topic')
                if original_topic:
                    safe_name = InputValidator.sanitize_project_name(original_topic)
                    download_filename = f"{safe_name}.mp4"
                else:
                    original_title = metadata.get('title')
                    if original_title:
                        safe_name = InputValidator.sanitize_project_name(original_title)
                        download_filename = f"{safe_name}.mp4"
            except Exception as e:
                print(f"Could not read metadata for {video_name}: {e}")
        
        return send_file(video_path, as_attachment=True, download_name=download_filename)
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error downloading video: {e}")
        return jsonify({"error": "Failed to download video"}), 500


@video_bp.route('/download/thumbnail/<video_name>', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_thumbnail(video_name):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        video_name = validate_video_name(video_name)
        
        thumbnail_path = OUTPUT_DIR / video_name / "thumbnail.jpg"
        if thumbnail_path.exists():
            return send_file(thumbnail_path, as_attachment=True, download_name=f"{video_name}_thumbnail.jpg")
        else:
            return jsonify({"error": "Thumbnail not found"}), 404
            
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
        return jsonify({"error": "Failed to download thumbnail"}), 500


@video_bp.route('/metadata/<video_name>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_metadata(video_name):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        video_name = validate_video_name(video_name)
        
        metadata_path = OUTPUT_DIR / video_name / "youtube_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return jsonify(metadata)
            except Exception as e:
                print(f"Error reading metadata: {e}")
                return jsonify({"error": "Failed to read metadata"}), 500
        else:
            return jsonify({"error": "Metadata not found"}), 404
            
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@video_bp.route('/download/metadata/<video_name>', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_metadata(video_name):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        video_name = validate_video_name(video_name)
        
        json_path = OUTPUT_DIR / video_name / "youtube_metadata.json"
        if not json_path.exists():
            return jsonify({"error": "Metadata not found"}), 404

        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        text_content = metadata.get('description', 'No Description Found')
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as temp_file:
            temp_file.write(text_content)
            temp_path = temp_file.name
        
        return send_file(temp_path, as_attachment=True, download_name=f"{video_name}_youtube_description.txt")
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error creating metadata text: {e}")
        return jsonify({"error": "Failed to create metadata file"}), 500