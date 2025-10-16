import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import initialize_apis, OUTPUT_DIR, ALLOWED_ORIGINS
from routes.content import content_bp
from routes.generation import generation_bp
from routes.usage import usage_bp
from routes.videos import video_bp
from routes.frontend import frontend_bp

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

initialize_apis()

app.register_blueprint(content_bp)
app.register_blueprint(generation_bp)
app.register_blueprint(usage_bp)
app.register_blueprint(video_bp)
app.register_blueprint(frontend_bp)

@app.route('/videos/<path:path>')
def serve_video(path):
    return send_from_directory(OUTPUT_DIR, path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(debug=False, port=port, host='0.0.0.0')