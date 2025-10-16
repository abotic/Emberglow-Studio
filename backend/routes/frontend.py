from flask import Blueprint, jsonify, send_from_directory
from flask_cors import cross_origin
from pathlib import Path

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
@cross_origin()
def serve_frontend():
    static_dir = Path('static')
    index_file = static_dir / 'index.html'
    if index_file.exists():
        return send_from_directory('static', 'index.html')
    else:
        return jsonify({"message": "Frontend not built. Run 'cd frontend && npm run build' first"}), 404

@frontend_bp.route('/<path:path>')
@cross_origin()
def serve_frontend_routes(path):
    if path.startswith('api/') or path.startswith('videos/'):
        return "Not Found", 404
    
    static_dir = Path('static')
    static_path = static_dir / path
    if static_path.exists() and static_path.is_file():
        return send_from_directory('static', path)
    
    index_file = static_dir / 'index.html'
    if index_file.exists():
        return send_from_directory('static', 'index.html')
    else:
        return jsonify({"message": "Frontend not built"}), 404