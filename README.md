# 🕶️ LuxeMirror: Real-Time Virtual Sunglasses Try-On

A stylish full-stack web application using **MediaPipe Face Mesh** to place luxury sunglasses on a user's face in real-time.

## 🚀 Features
- **Real-time Tracking**: High-precision face landmark detection using MediaPipe.
- **Dynamic Overlay**: Sunglasses scale and rotate automatically based on head position.
- **Multiple Styles**: Choose between Aviator, Wayfarer, and Luxury Round styles.
- **Capture & Save**: Take a screenshot that saves locally and sends to the Flask backend.
- **Premium UI**: Modern dark-themed design with smooth animations.

---

## 🛠️ Tech Stack
- **Frontend**: React (Vite), MediaPipe JS, Lucide Icons, Vanilla CSS.
- **Backend**: Python (Flask), Flask-CORS.

---

## 📦 Setup Instructions

### 1. Backend Setup
1. Open a terminal in the `backend/` directory.
2. Install dependencies:
   ```bash
   pip install flask flask-cors werkzeug
   ```
3. Run the server:
   ```bash
   python app.py
   ```
   *(Note: Ensure you are inside the `backend` folder when running this command)*
   *The backend will run on `http://localhost:5000`.*

### 2. Frontend Setup
1. Open a terminal in the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the displayed URL (usually `http://localhost:5173`).

---

## 📸 MediaPipe Implementation Details
- **Landmarks Used**: 
  - `33` & `263`: Outer corners of the eyes (for width and rotation).
  - `168`: Nose bridge (for positioning).
- **Optimization**: Uses `requestAnimationFrame` for buttery-smooth 60FPS rendering on the canvas.

## 🖼️ Assets
Assets are stored in `frontend/public/` and are preloaded during initialization to ensure zero lag when switching styles.

---
*Created with ❤️ by Antigravity*
