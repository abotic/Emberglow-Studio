import re
import bleach
from typing import Dict, Any


class ValidationError(Exception):
    pass


class InputValidator:
    PROJECT_NAME_PATTERN = re.compile(r'^[\w\s\-]+$')
    
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
        r'(--|\#|\/\*|\*\/)',
        r'(\bOR\b.*=.*)',
        r'(\bAND\b.*=.*)',
        r'(;.*--)',
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\.',
        r'\/\.\.',
        r'\.\.\/',
        r'%2e%2e',
        r'\.\.%2f',
    ]
    
    @staticmethod
    def sanitize_topic(topic: str, min_length: int = 5, max_length: int = 500) -> str:
        if not topic or not isinstance(topic, str):
            raise ValidationError("Topic must be a non-empty string")
        
        topic = topic.strip()
        
        if len(topic) < min_length:
            raise ValidationError(f"Topic must be at least {min_length} characters")
        
        if len(topic) > max_length:
            raise ValidationError(f"Topic must be less than {max_length} characters")
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, topic, re.IGNORECASE):
                raise ValidationError("Topic contains prohibited patterns")
        
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, topic, re.IGNORECASE):
                raise ValidationError("Topic contains prohibited path patterns")
        
        topic = bleach.clean(topic, tags=[], strip=True)
        topic = topic.replace('\x00', '')
        topic = ' '.join(topic.split())
        
        return topic
    
    @staticmethod
    def validate_video_type(video_type: str) -> str:
        valid_types = ['shorts', 'standard', 'longform']
        
        if not video_type or not isinstance(video_type, str):
            raise ValidationError("Video type must be a string")
        
        video_type = video_type.lower().strip()
        
        if video_type not in valid_types:
            raise ValidationError(f"Invalid video type. Must be one of: {valid_types}")
        
        return video_type
    
    @staticmethod
    def validate_category(category: str) -> str:
        valid_categories = ['why', 'what_if', 'hidden_truths', 'custom']
        
        if not category or not isinstance(category, str):
            raise ValidationError("Category must be a string")
        
        category = category.lower().strip()
        
        if category not in valid_categories:
            raise ValidationError(f"Invalid category. Must be one of: {valid_categories}")
        
        return category
    
    @staticmethod
    def validate_visual_mode(visual_mode: str) -> str:
        valid_modes = ['stability', 'stock']
        
        if not visual_mode or not isinstance(visual_mode, str):
            raise ValidationError("Visual mode must be a string")
        
        visual_mode = visual_mode.lower().strip()
        
        if visual_mode not in valid_modes:
            raise ValidationError(f"Invalid visual mode. Must be one of: {valid_modes}")
        
        return visual_mode
    
    @staticmethod
    def validate_voice_id(voice_id: str) -> str:
        if not voice_id or not isinstance(voice_id, str):
            raise ValidationError("Voice ID must be a string")
        
        voice_id = voice_id.strip()
        
        if not re.match(r'^[a-zA-Z0-9]{10,30}$', voice_id):
            raise ValidationError("Invalid voice ID format")
        
        return voice_id
    
    @staticmethod
    def validate_style_preset(style_preset: str) -> str:
        valid_presets = [
            'cinematic', 'photographic', 'anime', 'fantasy-art', 
            'digital-art', 'comic-book', 'analog-film', '3d-model',
            'line-art', 'low-poly', 'neon-punk'
        ]
        
        if not style_preset or not isinstance(style_preset, str):
            raise ValidationError("Style preset must be a string")
        
        style_preset = style_preset.lower().strip()
        
        if style_preset not in valid_presets:
            raise ValidationError(f"Invalid style preset. Must be one of: {valid_presets}")
        
        return style_preset
    
    @staticmethod
    def sanitize_project_name(name: str) -> str:
        if not name or not isinstance(name, str):
            raise ValidationError("Project name must be a non-empty string")
        
        name = name.strip()
        
        if '..' in name or '/' in name or '\\' in name:
            raise ValidationError("Project name contains invalid characters")
        
        name = re.sub(r'[^\w\s\-]', '', name)
        name = name.replace(' ', '_')
        name = re.sub(r'_+', '_', name)
        
        if not name:
            raise ValidationError("Project name is invalid after sanitization")
        
        if len(name) > 200:
            name = name[:200]
        
        return name.lower()
    
    @staticmethod
    def validate_progress_id(progress_id: str) -> str:
        if not progress_id or not isinstance(progress_id, str):
            raise ValidationError("Progress ID must be a string")
        
        progress_id = progress_id.strip()
        
        if not re.match(r'^[a-z_]+_\d+$', progress_id):
            raise ValidationError("Invalid progress ID format")
        
        return progress_id
    
    @staticmethod
    def validate_generation_request(data: Dict[str, Any]) -> Dict[str, Any]:
        validated = {}
        
        validated['topic'] = InputValidator.sanitize_topic(data.get('topic', ''))
        validated['category'] = InputValidator.validate_category(data.get('category', 'custom'))
        validated['video_type'] = InputValidator.validate_video_type(data.get('video_type', 'standard'))
        validated['generation_mode'] = InputValidator.validate_visual_mode(data.get('generation_mode', 'stock'))
        
        try:
            validated['voice_id'] = InputValidator.validate_voice_id(data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        except ValidationError:
            validated['voice_id'] = '21m00Tcm4TlvDq8ikWAM'
        
        try:
            validated['style_preset'] = InputValidator.validate_style_preset(data.get('style_preset', 'cinematic'))
        except ValidationError:
            validated['style_preset'] = 'cinematic'
        
        ai_provider = data.get('ai_provider')
        if ai_provider:
            validated['ai_provider'] = InputValidator.validate_visual_mode(ai_provider)
        
        return validated