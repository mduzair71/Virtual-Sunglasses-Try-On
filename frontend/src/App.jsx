import React, { useEffect, useRef, useState, useCallback } from 'react';
import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';
import { Camera, RefreshCw, ShoppingCart, ChevronRight } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const SUNGLASSES_STYLES = [
  { id: 'wayfarer', name: 'Modern Wayfarer', file: '/wayfarer.png', scale: 2.1, offset: 1.1, preferred_shape: 'Round/Oval' },
  { id: 'aviator', name: 'Classic Aviator', file: '/aviator.png', scale: 2.2, offset: 1.15, preferred_shape: 'Square/Heart' },
  { id: 'round', name: 'Luxury Round', file: '/round.png', scale: 2.0, offset: 1.2, preferred_shape: 'Square/Angular' },
];

const App = () => {
  const [activeStyleIdx, setActiveStyleIdx] = useState(0);
  const activeStyleRef = useRef(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [analysis, setAnalysis] = useState({ score: 0, status: 'Detecting...', shape: 'Analyzing' });

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const landmarkerRef = useRef(null);
  const requestRef = useRef();
  const imagesRef = useRef({});

  const currentStyle = SUNGLASSES_STYLES[activeStyleIdx];

  useEffect(() => {
    activeStyleRef.current = activeStyleIdx;
  }, [activeStyleIdx]);

  // Preload Sunglasses Images
  useEffect(() => {
    SUNGLASSES_STYLES.forEach(style => {
      if (!imagesRef.current[style.file]) {
        const img = new Image();
        img.src = style.file;
        imagesRef.current[style.file] = img;
      }
    });
  }, []);

  // Initialize MediaPipe Face Mesh
  useEffect(() => {
    const initDetector = async () => {
      try {
        const filesetResolver = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        const landmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU"
          },
          runningMode: "VIDEO",
          numFaces: 1
        });
        landmarkerRef.current = landmarker;
        setIsLoading(false);
      } catch (error) {
        console.error("MediaPipe Init Error:", error);
      }
    };
    initDetector();
  }, []);

  const startCamera = async () => {
    if (videoRef.current) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720, facingMode: "user" }
        });
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          setIsCameraActive(true);
          requestRef.current = requestAnimationFrame(renderLoop);
        };
      } catch (err) {
        console.error("Camera access denied:", err);
      }
    }
  };

  const renderLoop = useCallback((timestamp) => {
    if (!videoRef.current || !canvasRef.current || !landmarkerRef.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    // Draw Video Frame (Mirrored)
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    ctx.save();
    ctx.scale(-1, 1);
    ctx.translate(-canvasRef.current.width, 0);
    ctx.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
    ctx.restore();

    // AI Analysis
    const results = landmarkerRef.current.detectForVideo(videoRef.current, timestamp);
    
    if (results.faceLandmarks && results.faceLandmarks.length > 0) {
      processFace(results.faceLandmarks[0], ctx);
    } else {
      setAnalysis(prev => ({ ...prev, status: 'Searching...', score: 0 }));
    }

    requestRef.current = requestAnimationFrame(renderLoop);
  }, []);

  const processFace = (landmarks, ctx) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const w = canvas.width;
    const h = canvas.height;

    const getPos = (pt) => ({ x: (1 - pt.x) * w, y: pt.y * h });

    // Key points
    const leftEye = getPos(landmarks[33]);
    const rightEye = getPos(landmarks[263]);
    const noseBridge = getPos(landmarks[168]);
    const forehead = getPos(landmarks[10]);
    const chin = getPos(landmarks[152]);
    const leftCheek = getPos(landmarks[234]);
    const rightCheek = getPos(landmarks[454]);

    // Calculate face shape
    const faceH = Math.abs(forehead.y - chin.y);
    const faceW = Math.abs(leftCheek.x - rightCheek.x);
    const ratio = faceH / faceW;

    let shape = 'OVAL';
    if (ratio > 1.35) shape = 'OBLONG';
    else if (ratio < 1.15) shape = 'ROUND';
    else if (ratio < 1.3) shape = 'HEART';

    // Scoring logic
    const currentStyle = SUNGLASSES_STYLES[activeStyleRef.current];
    let score = 85; // Base score
    if (currentStyle.id === 'wayfarer' && (shape === 'ROUND' || shape === 'OVAL')) score = 95;
    if (currentStyle.id === 'round' && (shape === 'HEART' || shape === 'OBLONG')) score = 92;
    
    setAnalysis({ 
      score, 
      status: score > 90 ? 'PERFECT FIT' : 'GOOD MATCH',
      shape: shape 
    });

    // Draw Sunglasses
    const eyeDist = Math.sqrt(Math.pow(rightEye.x - leftEye.x, 2) + Math.pow(rightEye.y - leftEye.y, 2));
    const angle = Math.atan2(rightEye.y - leftEye.y, rightEye.x - leftEye.x);
    const glassesImg = imagesRef.current[currentStyle.file];

    if (glassesImg && glassesImg.complete) {
      const gWidth = eyeDist * currentStyle.scale;
      const gHeight = glassesImg.height * (gWidth / glassesImg.width);

      ctx.save();
      ctx.translate((leftEye.x + rightEye.x) / 2, (leftEye.y + rightEye.y) / 2 + (noseBridge.y - (leftEye.y + rightEye.y) / 2) * 0.15);
      ctx.rotate(angle);
      ctx.drawImage(glassesImg, -gWidth / 2, -gHeight / 2, gWidth, gHeight);
      ctx.restore();
    }
  };

  const handleBuy = async () => {
    alert(`Order placed for ${currentStyle.name}! Check backend for capture.`);
    // You can send a capture to the backend here similar to previous version
  };

  return (
    <div className="app-container">
      <div className="mirror-viewport">
        <video ref={videoRef} className="webcam-video" playsInline muted />
        <canvas ref={canvasRef} width={1280} height={720} className="overlay-canvas" />
      </div>

      {!isCameraActive && !isLoading && (
        <div className="init-overlay">
          <h1 style={{fontSize: '3rem', letterSpacing: '0.2em'}}>AI SUNGLASS <span style={{color:'var(--primary)'}}>BOUTIQUE</span></h1>
          <p style={{color: 'var(--text-muted)'}}>High-precision facial analysis for the perfect fit.</p>
          <button onClick={startCamera} className="btn-init">Enter Boutique</button>
        </div>
      )}

      {isCameraActive && (
        <div className="hud-overlay fade-in">
          <div className="hud-top">
            <div className="product-info">
              <div className="label">Product:</div>
              <h1 className="product-name">{currentStyle.name}</h1>
              
              <div className="styling-score">
                 <div className="label">Styling Score:</div>
                 <div className="score-value">
                   {analysis.score}%
                   <span className="score-status">— {analysis.status}</span>
                 </div>
                 <div className="nav-hint">[N] Next Style [B] Buy Now</div>
              </div>
            </div>

            <div style={{background: 'var(--glass)', padding: '16px', borderRadius: '4px', textAlign: 'right'}}>
               <div className="label">Face Geometry:</div>
               <div style={{fontSize: '18px', fontWeight: 'bold'}}>{analysis.shape} PROFILE</div>
               <div className="label" style={{marginTop: '8px'}}>Tracking: <span style={{color: 'var(--primary)'}}>Active</span></div>
            </div>
          </div>

          <div className="hud-bottom">
            <div className="controls-panel">
               <div style={{display: 'flex', gap: '10px'}}>
                  <select 
                    className="style-selector"
                    value={activeStyleIdx}
                    onChange={(e) => setActiveStyleIdx(Number(e.target.value))}
                  >
                    {SUNGLASSES_STYLES.map((s, i) => <option key={s.id} value={i}>{s.name}</option>)}
                  </select>
                  <button onClick={() => setActiveStyleIdx((activeStyleIdx + 1) % SUNGLASSES_STYLES.length)} className="style-selector">
                    <RefreshCw size={14} />
                  </button>
               </div>
            </div>

            <button onClick={handleBuy} className="buy-button">
              BUY NOW
            </button>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="init-overlay">
          <div className="status-dot" style={{width: '40px', height: '40px', animation: 'pulse 1s infinite'}} />
          <div className="label">Calibrating Vision Core...</div>
        </div>
      )}
    </div>
  );
};

export default App;
