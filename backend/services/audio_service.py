import os
import numpy as np
from pathlib import Path
from typing import List

from moviepy import AudioFileClip, AudioClip, concatenate_audioclips
from elevenlabs import generate

from config import SCRIPT_CHUNK_LIMIT
from core.models import AudioGenerationError

def generate_voiceover(script: str, project_dir: Path, video_type: str, voice_id: str, tts_model: str) -> str:
    audio_path = project_dir / "audio" / "narration.mp3"
    
    try:
        _generate_voiceover_elevenlabs(script, audio_path, project_dir, voice_id, tts_model)
        
        with AudioFileClip(str(audio_path)) as audio_clip:
            duration = audio_clip.duration
        
        if duration < 1.0:
            raise AudioGenerationError(f"Generated audio is too short: {duration}s")
            
        print(f"Audio generated successfully: {duration:.1f}s")
        return str(audio_path)
        
    except AudioGenerationError:
        raise
    except Exception as e:
        raise AudioGenerationError(f"TTS generation failed: {e}")

def _generate_voiceover_elevenlabs(script: str, audio_path: Path, project_dir: Path, voice_id: str, tts_model: str) -> None:
    audio_parts_dir = project_dir / "audio" / "parts"
    audio_parts_dir.mkdir(exist_ok=True)
    script_chunks = _split_text_into_chunks(script, SCRIPT_CHUNK_LIMIT)
    audio_part_files = []
    
    if len(script_chunks) > 1:
        print(f"Script is long, splitting into {len(script_chunks)} chunks for ElevenLabs.")
    
    clips = []
    try:
        for i, chunk in enumerate(script_chunks):
            print(f"   - Generating audio for chunk {i+1}/{len(script_chunks)}...")
            audio_data = generate(text=chunk, voice=voice_id, model=tts_model)
            part_path = audio_parts_dir / f"part_{i}.mp3"
            with open(part_path, 'wb') as f:
                f.write(audio_data)
            audio_part_files.append(str(part_path))
        
        if len(audio_part_files) > 1:
            print("Stitching ElevenLabs audio chunks together...")
            clips = [AudioFileClip(file) for file in audio_part_files]
            final_audio = concatenate_audioclips(clips)
            final_audio = audio_normalize(final_audio)
            final_audio.write_audiofile(str(audio_path), codec='mp3')
            final_audio.close()
        else:
            os.rename(audio_part_files[0], audio_path)
    finally:
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        if audio_parts_dir.exists():
            for part_file in audio_parts_dir.glob("*.mp3"):
                try:
                    os.remove(part_file)
                except:
                    pass
            try:
                os.rmdir(audio_parts_dir)
            except:
                pass

def _split_text_into_chunks(text: str, chunk_limit: int) -> List[str]:
    chunks = []
    while len(text) > chunk_limit:
        split_pos = text.rfind('.', 0, chunk_limit)
        if split_pos == -1: split_pos = text.rfind('?', 0, chunk_limit)
        if split_pos == -1: split_pos = text.rfind('!', 0, chunk_limit)
        if split_pos == -1: split_pos = text.rfind(' ', 0, chunk_limit)
        if split_pos == -1: split_pos = chunk_limit
        chunk = text[:split_pos+1]
        chunks.append(chunk)
        text = text[split_pos+1:]
    chunks.append(text)
    return [c.strip() for c in chunks if c.strip()]

def audio_normalize(audio_clip):
    try:
        audio_array = audio_clip.to_soundarray(fps=44100)
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val * 0.9
        return AudioClip(
            lambda t: audio_array[int(t * 44100)] if int(t * 44100) < len(audio_array) else 0,
            duration=audio_clip.duration,
            fps=44100
        )
    except Exception as e:
        print(f"Audio normalization failed: {e}")
        return audio_clip