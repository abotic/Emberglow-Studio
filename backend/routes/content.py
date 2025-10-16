import base64
import os
import tempfile
import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from elevenlabs import generate

from config import ELEVENLABS_API_KEY
from constants import WHY_TOPICS, WHAT_IF_TOPICS, HIDDEN_TRUTHS_TOPICS
from repositories.progress_repository import load_progress
from utils.validation import InputValidator, ValidationError

content_bp = Blueprint('content_api', __name__, url_prefix='/api')

@content_bp.route('/topics', methods=['GET', 'OPTIONS'])
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

@content_bp.route('/voices', methods=['GET', 'OPTIONS'])  
@cross_origin()
def get_voices():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    fallback_voices = [
        {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel - Suggested", "category": "premade", "description": "Calm, young adult female", "recommended_for": ["standard", "why", "what_if"]},
        {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "category": "premade", "description": "Well-rounded, young adult male", "recommended_for": ["standard", "hidden_truths"]},
        {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "category": "premade", "description": "Crisp, middle-aged male", "recommended_for": ["standard", "shorts"]},
    ]
    
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            raise Exception(f"API call failed with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return jsonify({"voices": fallback_voices})

@content_bp.route('/test-voice', methods=['POST', 'OPTIONS'])
@cross_origin()
def test_voice():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        voice_id = InputValidator.validate_voice_id(data.get('voice_id'))
        video_type = InputValidator.validate_video_type(data.get('video_type', 'standard'))
        
        test_text = "Did you know this mind-blowing fact?" if video_type == 'shorts' else "Hello! This is how I sound. I'm ready to narrate your videos."
        
        audio = generate(text=test_text, voice=voice_id, model="eleven_monolingual_v1")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio)
            temp_path = temp_file.name
        
        with open(temp_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        os.unlink(temp_path)
        
        return jsonify({"audio_base64": audio_base64})
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to generate voice test"}), 500