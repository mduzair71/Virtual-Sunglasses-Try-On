"""
AI Virtual Sunglass Boutique: Try-On & Buy Engine
=================================================
This model integrates the concept: 1. SELECT → 2. TRY-ON → 3. SUITABILITY → 4. BUY.

Key AI Logic:
- MULTI-STYLE: Press 'N' to cycle through the Sunglasses.
- REAL-TIME SUITABILITY: Checks if your Face Shape matches the CURRENT Frame.
- ORDER TRIGGER: Only enables 'ORDER' if the Match Score is high enough.
- INTERACTIVE SHOPPING: Simulates a premium online store experience.
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import time
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import RunningMode
from mediapipe import Image, ImageFormat

# ─────────────────────────────────────────────
# Product Catalog (Styles)
# ─────────────────────────────────────────────
CATALOG = [
    {"name": "CLASSIC AVIATOR", "file": "sunglasses.png", "target": "ROUND/OVAL"},
    {"name": "MODERN WAYFARER", "file": "wayfarer.png", "target": "SQUARE/HEART"}
]

MODEL_PATH = "face_landmarker.task"

# Landmarks
LM_FOREHEAD = 10; LM_CHIN = 152; LM_L_CHEEK = 234; LM_R_CHEEK = 454
LM_L_EYE = 33; LM_R_EYE = 263; LM_N_BRIDGE = 168
LM_L_JAW = 132; LM_R_JAW = 361

# ─────────────────────────────────────────────
# The AI Stylist Engine
# ─────────────────────────────────────────────
class AIStoreEngine:
    def __init__(self):
        self.current_idx = 0
        self.face_shape = "Detecting..."
        self.match_score = 0
        self.status = "CHECKING..."
        self.is_bought = False

    def next_style(self):
        self.current_idx = (self.current_idx + 1) % len(CATALOG)
        self.is_bought = False

    def get_current(self):
        return CATALOG[self.current_idx]

    def analyze_suitability(self, lms):
        """Logic: Cross-reference face geometry with product geometry."""
        h = np.linalg.norm(np.array(lms[LM_FOREHEAD]) - np.array(lms[LM_CHIN]))
        w = np.linalg.norm(np.array(lms[LM_L_CHEEK]) - np.array(lms[LM_R_CHEEK]))
        ratio = h / max(w, 1)

        # Detect Face Shape
        if ratio > 1.35: self.face_shape = "OVAL"
        elif ratio < 1.15: self.face_shape = "ROUND"
        else: self.face_shape = "HEART/SQUARE"

        # Match Logic for Catalog
        item = self.get_current()
        if item["name"] == "CLASSIC AVIATOR":
            self.match_score = 95 if self.face_shape in ["OVAL", "ROUND"] else 60
        else: # WAYFARER
            self.match_score = 90 if self.face_shape in ["HEART/SQUARE", "OVAL"] else 65

        # Decision Output
        if self.match_score >= 85:
            self.status = "PERFECT FIT"
        elif self.match_score >= 70:
            self.status = "GOOD MATCH"
        else:
            self.status = "TRY ANOTHER"

    def buy_action(self):
        if self.match_score >= 80:
            self.is_bought = True
            return True
        return False

# ─────────────────────────────────────────────
# UI & Rendering
# ─────────────────────────────────────────────
def overlay_transparent(bg, overlay, x, y):
    """Safely overlays a BGRA image on a BGR background."""
    h, w = overlay.shape[:2]
    h2, w2 = bg.shape[:2]
    
    # 1. Coordinate Clipping
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, w2), min(y + h, h2)
    if x1 >= x2 or y1 >= y2: return bg
    
    # 2. Get ROI (Region of Interest)
    # Ensure overlay has 4 channels for alpha blending
    if overlay.shape[2] < 4:
        return bg # Skip if no alpha
        
    ov = overlay[y1-y:y2-y, x1-x:x2-x]
    alpha = ov[:, :, 3:4] / 255.0
    
    # Perform blending only on colors
    bg_roi = bg[y1:y2, x1:x2].astype(float)
    ov_rgb = ov[:, :, :3].astype(float)
    
    blended = (1.0 - alpha) * bg_roi + alpha * ov_rgb
    bg[y1:y2, x1:x2] = blended.astype(np.uint8)
    return bg

def draw_boutique_ui(frame, engine):
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_DUPLEX
    
    # 🛒 Header: Store Name
    cv2.rectangle(frame, (0, 0), (w, 60), (20, 20, 20), -1)
    cv2.putText(frame, "AI SUNGLASS BOUTIQUE", (40, 40), font, 0.8, (255, 255, 255), 2)
    
    # 🏷️ Sidebar: Product Info
    product = engine.get_current()
    panel = frame.copy()
    cv2.rectangle(panel, (20, 80), (320, 240), (40, 40, 40), -1)
    cv2.addWeighted(panel, 0.7, frame, 0.3, 0, frame)
    
    cv2.putText(frame, "PRODUCT:", (35, 115), font, 0.5, (180, 180, 180), 1)
    cv2.putText(frame, product["name"], (35, 140), font, 0.7, (255, 255, 255), 2)
    
    cv2.putText(frame, "STYLING SCORE:", (35, 180), font, 0.5, (180, 180, 180), 1)
    color = (0, 255, 0) if engine.match_score >= 85 else (0, 215, 255)
    cv2.putText(frame, f"{engine.match_score}% - {engine.status}", (35, 205), font, 0.6, color, 2)
    
    # Selection Controls
    cv2.putText(frame, "[N] Next Style  [B] Buy Now  [Q] Exit", (35, 230), font, 0.4, (150, 150, 150), 1)

    # 💰 The BUY / ORDER Flow
    if engine.is_bought:
        cv2.rectangle(frame, (w//2-150, h//2-50), (w//2+150, h//2+50), (0, 180, 0), -1)
        cv2.putText(frame, "ORDER PLACED!", (w//2-110, h//2+15), font, 1, (255, 255, 255), 3)
    elif engine.match_score >= 85:
        pulse = int(abs(np.sin(time.time() * 3)) * 40) # Flashing effect
        cv2.rectangle(frame, (w-260, h-100), (w-40, h-40), (0, 150 + pulse, 0), -1)
        cv2.putText(frame, "BUY NOW", (w-205, h-60), font, 0.8, (255, 255, 255), 2)

# ─────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────
def main():
    # Load MediaPipe
    base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp_vision.FaceLandmarkerOptions(base_options=base_opts, running_mode=RunningMode.IMAGE)
    landmarker = mp_vision.FaceLandmarker.create_from_options(options)

    # Initialize Engine
    engine = AIStoreEngine()
    
    # Pre-load all styles and ensure BGRA
    style_imgs = {}
    for item in CATALOG:
        img = cv2.imread(item["file"], cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Warning: Could not load {item['file']}")
            continue
            
        # FORCE ALPHA CHANNEL (Ensure 4 channels)
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            
        style_imgs[item["name"]] = img

    cap = cv2.VideoCapture(0)
    print("\n[AI Boutique Engine Loaded]")
    print("Toggle through styles using 'N' to find your perfect match.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # AI Detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = Image(image_format=ImageFormat.SRGB, data=rgb)
        res = landmarker.detect(mp_img)

        if res.face_landmarks:
            face_lms = res.face_landmarks[0]
            lms = {i: (int(pt.x * w), int(pt.y * h)) for i, pt in enumerate(face_lms)}
            
            # Analyze & Fit
            engine.analyze_suitability(lms)
            
            p_l, p_r, p_n = lms[LM_L_EYE], lms[LM_R_EYE], lms[LM_N_BRIDGE]
            e_w = np.linalg.norm(np.array(p_r) - np.array(p_l))
            ang = np.degrees(np.arctan2(p_r[1] - p_l[1], p_r[0] - p_l[0]))

            # Get current overlay
            glasses_img = style_imgs[engine.get_current()["name"]]
            gw = int(e_w * 1.55)
            gh = int(glasses_img.shape[0] * (gw / glasses_img.shape[1]))
            resized = cv2.resize(glasses_img, (gw, gh))
            
            M = cv2.getRotationMatrix2D((gw//2, gh//2), ang, 1)
            rotated = cv2.warpAffine(resized, M, (gw, gh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

            px = int((p_l[0] + p_r[0]) / 2 - gw / 2)
            py = int((p_l[1] + p_r[1]) / 2 - gh / 2 + (p_n[1] - (p_l[1] + p_r[1])/2) * 0.15)
            
            frame = overlay_transparent(frame, rotated, px, py)

        draw_boutique_ui(frame, engine)
        cv2.imshow("AI SUNGLASS BOUTIQUE", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('n'): engine.next_style()
        elif key == ord('b'): engine.buy_action()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()