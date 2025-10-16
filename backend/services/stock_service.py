import os
import time
import requests
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional

from config import PEXELS_API_KEY, MAX_DOWNLOAD_WORKERS

def search_pexels(query: str, per_page: int = 5) -> List[Dict]:
    headers = {"Authorization": PEXELS_API_KEY}
    results = []
    
    try:
        params = {"query": query, "per_page": per_page, "orientation": "landscape", "size": "medium"}
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
        response.raise_for_status()
        for v in response.json().get("videos", []):
            hd_file = next((f for f in v.get("video_files", []) if 1280 <= f.get("width", 0) <= 1920), None)
            if hd_file and hd_file.get("link"):
                results.append({"type": "video", "url": hd_file["link"], "id": f"pexels_v_{v['id']}"})
    except Exception as e:
        print(f"Pexels video search failed for '{query}': {e}")
        
    try:
        params = {"query": query, "per_page": per_page, "orientation": "landscape"}
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        response.raise_for_status()
        for p in response.json().get("photos", []):
            results.append({"type": "image", "url": p["src"]["large2x"], "id": f"pexels_i_{p['id']}"})
    except Exception as e:
        print(f"Pexels image search failed for '{query}': {e}")
        
    return results

def download_asset(asset_info: tuple) -> Optional[str]:
    index, asset, project_dir = asset_info
    ext = "mp4" if asset["type"] == "video" else "jpg"
    filename = f"asset_{index}_{asset['id']}.{ext}"
    filepath = project_dir / "assets" / filename

    if filepath.exists() and filepath.stat().st_size > 1000:
        return str(filepath)

    for attempt in range(3):
        try:
            response = requests.get(asset["url"], stream=True, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if filepath.stat().st_size > 1000:
                return str(filepath)
            else:
                filepath.unlink()
                return None
        except requests.exceptions.RequestException:
            if attempt < 2:
                time.sleep(0.5)
            else:
                return None
    return None

def download_assets_parallel(assets: List[Dict], project_dir: Path) -> List[str]:
    downloaded_paths = []
    asset_tuples = [(i, asset, project_dir) for i, asset in enumerate(assets)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
        future_to_asset = {executor.submit(download_asset, asset_tuple): asset_tuple for asset_tuple in asset_tuples}
        for future in concurrent.futures.as_completed(future_to_asset):
            result = future.result()
            if result:
                downloaded_paths.append(result)
                print(f"✓ Downloaded: {os.path.basename(result)}")
                
    return downloaded_paths