import threading
import time
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from core.generator import VideoGenerator, get_progress
from core.models import GenerationConfig
from utils.resource_monitor import ResourceMonitor
from utils.validation import InputValidator, ValidationError

generation_bp = Blueprint('generation_api', __name__, url_prefix='/api')

@generation_bp.route('/generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_video():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    if not ResourceMonitor.can_start_new_video():
        return jsonify({"error": "System busy. Please try again shortly."}), 429
    
    try:
        data = request.json
        validated_data = InputValidator.validate_generation_request(data)
        
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
        
        thread = threading.Thread(target=lambda: VideoGenerator(config).generate(), daemon=True)
        thread.start()
        
        return jsonify({"progress_id": progress_id, "video_type": validated_data['video_type']})
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to start video generation"}), 500

@generation_bp.route('/progress/<progress_id>', methods=['GET', 'OPTIONS'])
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