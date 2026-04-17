"""
Auto-downloads the MediaPipe FaceLandmarker model file if not present.
"""
import urllib.request
import os

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = "face_landmarker.task"

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"[OK] Model already exists: {MODEL_PATH}")
        return True
    print(f"[Downloading] Face Landmarker model...")
    print(f"  Source: {MODEL_URL}")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=_progress)
        print(f"\n[OK] Model saved to: {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to download model: {e}")
        return False

def _progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(downloaded / total_size * 100, 100)
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        print(f"\r  Progress: {pct:.1f}% ({mb_done:.1f}/{mb_total:.1f} MB)", end="", flush=True)

if __name__ == "__main__":
    download_model()
