import json
import os
import tempfile
import time
import fcntl
from threading import RLock
from pathlib import Path
from typing import Dict, Any
from config import PROGRESS_FILE, GENERATING_VIDEOS_FILE


_lock = RLock()
_progress_cache = {"data": None, "timestamp": 0}
_generating_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 1.0


def _acquire_file_lock(file_handle, timeout=5.0):
    start_time = time.time()
    while True:
        try:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.01)


def _release_file_lock(file_handle):
    try:
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    except (IOError, OSError):
        pass


def _read_json_with_lock(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            if not _acquire_file_lock(f, timeout=5.0):
                print(f"Warning: Could not acquire lock for {path}, using default")
                return default
            
            try:
                content = f.read()
                if not content.strip():
                    return default
                data = json.loads(content)
                return data if isinstance(data, type(default)) else default
            finally:
                _release_file_lock(f)
    except json.JSONDecodeError as e:
        print(f"Warning: JSON decode error in {path}: {e}")
        return default
    except Exception as e:
        print(f"Warning: Error reading {path}: {e}")
        return default


def _atomic_write_with_lock(path: Path, data: Any) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = None
    tmp_path = None
    
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True
        )
        
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            fd = None
            
            if not _acquire_file_lock(tmp, timeout=5.0):
                print(f"Warning: Could not acquire lock for writing {path}")
                return False
            
            try:
                json.dump(data, tmp, ensure_ascii=False, indent=2)
                tmp.flush()
                os.fsync(tmp.fileno())
            finally:
                _release_file_lock(tmp)
        
        os.replace(tmp_path, path)
        return True
        
    except Exception as e:
        print(f"Error writing {path}: {e}")
        return False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


def load_progress() -> Dict[str, Any]:
    with _lock:
        now = time.time()
        
        if (_progress_cache["data"] is not None and 
            now - _progress_cache["timestamp"] < CACHE_TTL):
            return _progress_cache["data"].copy()
        
        data = _read_json_with_lock(PROGRESS_FILE, {"completed": []})
        
        if "completed" not in data or not isinstance(data["completed"], list):
            data["completed"] = []
        
        _progress_cache["data"] = data
        _progress_cache["timestamp"] = now
        
        return data.copy()


def save_progress(data: Dict[str, Any]) -> bool:
    with _lock:
        if "completed" not in data or not isinstance(data["completed"], list):
            data["completed"] = []
        
        success = _atomic_write_with_lock(PROGRESS_FILE, data)
        
        if success:
            _progress_cache["data"] = data.copy()
            _progress_cache["timestamp"] = time.time()
        
        return success


def mark_video_completed(topic: str) -> bool:
    with _lock:
        data = load_progress()
        
        if topic not in data["completed"]:
            data["completed"].append(topic)
            return save_progress(data)
        
        return True


def is_video_completed(topic: str) -> bool:
    with _lock:
        data = load_progress()
        return topic in data["completed"]


def load_generating_videos() -> Dict[str, Any]:
    with _lock:
        now = time.time()
        
        if (_generating_cache["data"] is not None and 
            now - _generating_cache["timestamp"] < CACHE_TTL):
            return _generating_cache["data"].copy()
        
        data = _read_json_with_lock(GENERATING_VIDEOS_FILE, {})
        
        _generating_cache["data"] = data
        _generating_cache["timestamp"] = now
        
        return data.copy()


def save_generating_videos(obj: Dict[str, Any]) -> bool:
    with _lock:
        success = _atomic_write_with_lock(GENERATING_VIDEOS_FILE, obj)
        
        if success:
            _generating_cache["data"] = obj.copy()
            _generating_cache["timestamp"] = time.time()
        
        return success


def add_generating_video(project_name: str, topic: str, progress_id: str, video_type: str) -> bool:
    with _lock:
        data = load_generating_videos()
        
        if project_name in data:
            print(f"Warning: Project {project_name} already exists in generating videos")
        
        data[project_name] = {
            "topic": topic,
            "progress_id": progress_id,
            "video_type": video_type,
            "started_at": int(time.time())
        }
        
        return save_generating_videos(data)


def remove_generating_video(project_name: str) -> bool:
    with _lock:
        data = load_generating_videos()
        
        if project_name in data:
            del data[project_name]
            return save_generating_videos(data)
        
        return True


def cleanup_stale_generations(max_age_seconds: int = 3600) -> int:
    with _lock:
        data = load_generating_videos()
        now = int(time.time())
        removed = 0
        
        stale_projects = []
        for project_name, info in data.items():
            started_at = info.get("started_at", 0)
            if now - started_at > max_age_seconds:
                stale_projects.append(project_name)
        
        for project_name in stale_projects:
            del data[project_name]
            removed += 1
        
        if removed > 0:
            save_generating_videos(data)
            print(f"Cleaned up {removed} stale generation entries")
        
        return removed