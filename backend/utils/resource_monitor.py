import psutil
import gc

class ResourceMonitor:
    @staticmethod
    def get_system_stats():
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'disk_usage_percent': psutil.disk_usage('/').percent
        }

    @staticmethod
    def can_start_new_video():
        stats = ResourceMonitor.get_system_stats()
        
        if stats['memory_percent'] > 80 or stats['cpu_percent'] > 90:
            return False
        
        if stats['memory_available_gb'] < 2:
            return False
            
        return True

    @staticmethod
    def cleanup_memory():
        print("🧹 Forcing garbage collection...")
        gc.collect()