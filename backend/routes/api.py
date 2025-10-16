import os
import json
import time
import requests
import threading
import datetime
import tempfile
import base64
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from elevenlabs import generate

from config import ELEVENLABS_API_KEY, OPENAI_API_KEY, OUTPUT_DIR
from constants import WHY_TOPICS, WHAT_IF_TOPICS, HIDDEN_TRUTHS_TOPICS
from core.generator import VideoGenerator, get_progress
from core.models import GenerationConfig
from repositories.progress_repository import load_progress
from repositories.file_repository import get_folder_size, get_video_duration
from utils.resource_monitor import ResourceMonitor
from utils.validation import InputValidator, ValidationError

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/topics', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_topics():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    progress = load_progress()
    completed = progress.get("completed", [])
    
    return jsonify({
        "why": [{"title": t, "completed": t in completed} for t in WHY_TOPICS],
        "what_if": [{"title": t, "completed": t in completed} for t in WHAT_IF_TOPICS],
        "hidden_truths": [{"title": t, "completed": t in completed} for t in HIDDEN_TRUTHS_TOPICS],
    })


@api_bp.route('/voices', methods=['GET', 'OPTIONS'])  
@cross_origin()
def get_voices():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    fallback_voices = [
        {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel - Suggested", "category": "premade", "description": "Calm, young adult female", "recommended_for": ["standard", "why", "what_if"]},
        {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "category": "premade", "description": "Well-rounded, young adult male", "recommended_for": ["standard", "hidden_truths"]},
        {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "category": "premade", "description": "Crisp, middle-aged male", "recommended_for": ["standard", "shorts"]},
        {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "category": "premade", "description": "Soft, young adult female", "recommended_for": ["standard"]},
        {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "category": "premade", "description": "Strong, young adult female", "recommended_for": ["standard"]},
        {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "category": "premade", "description": "Deep, narrative male", "recommended_for": ["standard"]},
        {"voice_id": "flq6f7yk4E4fJM5XTYuZ", "name": "Michael", "category": "premade", "description": "Energetic, young male", "recommended_for": ["standard", "shorts"]},
    ]
    
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            fetched_voices = []
            fallback_ids = {v["voice_id"] for v in fallback_voices}
            
            for voice in data.get("voices", []):
                voice_id = voice.get("voice_id")
                if voice_id not in fallback_ids:
                    description = voice.get("description", "")
                    if len(description) > 50:
                        description = description[:47] + "..."
                    
                    fetched_voices.append({
                        "voice_id": voice_id,
                        "name": voice.get("name"),
                        "category": voice.get("category", "premade"),
                        "description": description,
                        "recommended_for": []
                    })
            
            all_voices = fallback_voices + fetched_voices
            return jsonify({"voices": all_voices})
        else:
            raise Exception(f"API call failed with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return jsonify({"voices": fallback_voices})


@api_bp.route('/test-voice', methods=['POST', 'OPTIONS'])
@cross_origin()
def test_voice():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        voice_id = data.get('voice_id')
        try:
            voice_id = InputValidator.validate_voice_id(voice_id)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        video_type = data.get('video_type', 'standard')
        try:
            video_type = InputValidator.validate_video_type(video_type)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        if video_type == 'shorts':
            test_text = "Did you know this mind-blowing fact? In just 30 seconds, I'll reveal something that will completely change how you see the world. Get ready to be amazed!"
        else:
            test_text = "Hello! This is how I sound. I'm ready to narrate your YouTube videos with clear, engaging speech that keeps viewers watching until the very end."
        
        audio = generate(text=test_text, voice=voice_id, model="eleven_monolingual_v1")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio)
            temp_path = temp_file.name
        
        with open(temp_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        os.unlink(temp_path)
        
        return jsonify({"audio_base64": audio_base64, "message": "Voice test generated successfully"})
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error testing voice: {e}")
        return jsonify({"error": "Failed to generate voice test"}), 500


@api_bp.route('/elevenlabs/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_elevenlabs_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        response = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "character_count": data.get("character_count", 0),
                "character_limit": data.get("character_limit", 10000),
                "can_extend_character_limit": data.get("can_extend_character_limit", False),
                "allowed_to_extend_character_limit": data.get("allowed_to_extend_character_limit", False),
                "next_character_count_reset_unix": data.get("next_character_count_reset_unix", 0),
                "voice_limit": data.get("voice_limit", 0),
                "max_voice_add_edits": data.get("max_voice_add_edits", 0),
                "voice_add_edit_counter": data.get("voice_add_edit_counter", 0),
                "professional_voice_limit": data.get("professional_voice_limit", 0),
                "can_extend_voice_limit": data.get("can_extend_voice_limit", False),
                "can_use_instant_voice_cloning": data.get("can_use_instant_voice_cloning", False),
                "can_use_professional_voice_cloning": data.get("can_use_professional_voice_cloning", False),
                "tier": data.get("tier", "Free"),
                "invoice_period": data.get("invoice_period", ""),
                "status": data.get("status", "active"),
            })
        else:
            raise Exception(f"API call failed with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching ElevenLabs usage: {e}")
        return jsonify({"error": "Could not fetch usage data"}), 500


@api_bp.route('/openai/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_openai_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        now = datetime.datetime.now()
        return jsonify({
            "status": "active",
            "current_month": now.strftime('%B %Y'),
            "total_cost_estimate": 0,
            "total_requests": 0,
            "balance_available": False,
            "note": "OpenAI balance requires special API access"
        })
    except Exception as e:
        print(f"Error with OpenAI usage: {e}")
        return jsonify({
            "status": "error",
            "current_month": datetime.datetime.now().strftime('%B %Y'),
            "total_cost_estimate": 0,
            "total_requests": 0,
            "balance_available": False,
            "error": "Could not fetch usage data"
        })


@api_bp.route('/generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_video():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    if not ResourceMonitor.can_start_new_video():
        return jsonify({"error": "System busy. Please try again shortly."}), 429
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        try:
            validated_data = InputValidator.validate_generation_request(data)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        progress_id = f"{validated_data['video_type']}_{validated_data['category']}_{int(time.time())}"
        
        config = GenerationConfig(
            topic=validated_data['topic'],
            category=validated_data['category'],
            progress_id=progress_id,
            voice_id=validated_data['voice_id'],
            generation_mode=validated_data['generation_mode'],
            video_type=validated_data['video_type'],
            ai_provider=validated_data.get('ai_provider', 'stability'),
            style_preset=validated_data['style_preset']
        )
        
        def run_generation():
            generator = VideoGenerator(config)
            generator.generate()
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
        
        return jsonify({"progress_id": progress_id, "video_type": validated_data['video_type']})
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error starting video generation: {e}")
        return jsonify({"error": "Failed to start video generation"}), 500


@api_bp.route('/progress/<progress_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_progress_route(progress_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        progress_id = InputValidator.validate_progress_id(progress_id)
        progress = get_progress(progress_id)
        return jsonify(progress)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route('/storage/usage', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_storage_usage():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        if not OUTPUT_DIR.exists():
            return jsonify({
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "total_size_gb": 0,
                "video_count": 0,
                "projects": []
            })
        
        total_size = 0
        video_count = 0
        projects = []
        video_type_counts = {"standard": 0, "shorts": 0}
        
        for project_dir in OUTPUT_DIR.iterdir():
            if project_dir.is_dir():
                project_size = get_folder_size(project_dir)
                total_size += project_size
                
                video_file = project_dir / "final_video.mp4"
                if video_file.exists():
                    video_count += 1
                    
                    video_type = "standard"
                    metadata_file = project_dir / "youtube_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                if "#Shorts" in metadata.get("title", ""):
                                    video_type = "shorts"
                        except:
                            duration = get_video_duration(video_file)
                            if duration and duration < 60:
                                video_type = "shorts"
                    
                    video_type_counts[video_type] += 1
                    
                    projects.append({
                        "name": project_dir.name,
                        "display_name": project_dir.name.replace('_', ' ').title(),
                        "size_bytes": project_size,
                        "size_mb": round(project_size / (1024 * 1024), 1),
                        "created": int(project_dir.stat().st_ctime),
                        "video_type": video_type
                    })
        
        return jsonify({
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 1),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "video_count": video_count,
            "video_type_counts": video_type_counts,
            "projects": sorted(projects, key=lambda x: x['created'], reverse=True)
        })
        
    except Exception as e:
        print(f"Error calculating storage usage: {e}")
        return jsonify({"error": "Could not calculate storage usage"}), 500


@api_bp.route('/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health_check():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    return jsonify({"status": "ok", "message": "Server is running"})


@api_bp.route('/system/status', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_system_status():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    from config import MAX_CONCURRENT_VIDEOS
    from core.generator import video_generation_semaphore
    
    stats = ResourceMonitor.get_system_stats()
    
    return jsonify({
        "system": stats,
        "video_generation": {
            "active": MAX_CONCURRENT_VIDEOS - video_generation_semaphore._value,
            "max_concurrent": MAX_CONCURRENT_VIDEOS,
            "can_start_new": ResourceMonitor.can_start_new_video()
        }
    })