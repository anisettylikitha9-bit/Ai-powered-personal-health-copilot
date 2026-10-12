import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Heart, Activity, Sparkles, Orbit } from 'lucide-react';

export default function ThreeHeartCanvas({ 
  bpm = 72, 
  height = "380px", 
  showControls = true,
  interactive = true 
}) {
  const containerRef = useRef(null);
  const [currentBpm, setCurrentBpm] = useState(bpm);
  const [viewMode, setViewMode] = useState('heart'); // 'heart' | 'dna' | 'both'
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const width = container.clientWidth || 600;
    const canvasHeight = container.clientHeight || 380;

    const camera = new THREE.PerspectiveCamera(50, width / canvasHeight, 0.1, 1000);
    camera.position.z = 32;

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, canvasHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      container.innerHTML = '';
      container.appendChild(renderer.domElement);
    } catch (e) {
      console.warn('WebGL initialization skipped:', e);
      return;
    }

    // 2. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x06b6d4, 3, 50); // Cyan
    pointLight1.position.set(10, 15, 15);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0xf43f5e, 2.5, 50); // Rose
    pointLight2.position.set(-10, -10, 15);
    scene.add(pointLight2);

    // 3. Heart Geometry Generation (3D Parametric Cloud & Wireframe)
    const heartGroup = new THREE.Group();
    scene.add(heartGroup);

    const heartVertices = [];
    const heartColors = [];
    const colorCyan = new THREE.Color(0x06b6d4);
    const colorRose = new THREE.Color(0xf43f5e);
    const colorTeal = new THREE.Color(0x14b8a6);

    const numPoints = 1600;
    for (let i = 0; i < numPoints; i++) {
      // Parametric 3D heart curve with noise volume
      const t = Math.PI * (2 * Math.random() - 1);
      const u = Math.PI * (Math.random() - 0.5);

      const x = 16 * Math.pow(Math.sin(t), 3);
      const y = 13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t);
      const z = (Math.sin(u) * 7.5) * (1 - Math.abs(t) / Math.PI * 0.4);

      // Add gentle random shell jitter for organic 3D cloud
      const jitter = 0.85 + Math.random() * 0.3;
      heartVertices.push(x * 0.65 * jitter, y * 0.65 * jitter, z * jitter);

      // Color gradient from teal bottom to rose heart core
      const mixRatio = (y + 15) / 30;
      const c = colorCyan.clone().lerp(colorRose, mixRatio);
      heartColors.push(c.r, c.g, c.b);
    }

    const heartGeo = new THREE.BufferGeometry();
    heartGeo.setAttribute('position', new THREE.Float32BufferAttribute(heartVertices, 3));
    heartGeo.setAttribute('color', new THREE.Float32BufferAttribute(heartColors, 3));

    // Custom Glowing Particle Material
    const heartMat = new THREE.PointsMaterial({
      size: 0.55,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });
    const heartPoints = new THREE.Points(heartGeo, heartMat);
    heartGroup.add(heartPoints);

    // Inner glowing core wireframe
    const coreGeo = new THREE.SphereGeometry(3.5, 18, 18);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x0284c7,
      wireframe: true,
      transparent: true,
      opacity: 0.25,
      blending: THREE.AdditiveBlending
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    coreMesh.position.y = 1;
    heartGroup.add(coreMesh);

    // 4. Double Helix DNA Strand
    const dnaGroup = new THREE.Group();
    scene.add(dnaGroup);

    const dnaPointsCount = 280;
    const dnaRadius = 9;
    const dnaHeight = 24;

    const strand1Vertices = [];
    const strand2Vertices = [];
    const rungsVertices = [];

    for (let i = 0; i < dnaPointsCount; i++) {
      const angle = (i / dnaPointsCount) * Math.PI * 8;
      const y = (i / dnaPointsCount - 0.5) * dnaHeight;
      const x1 = Math.cos(angle) * dnaRadius;
      const z1 = Math.sin(angle) * dnaRadius;
      const x2 = Math.cos(angle + Math.PI) * dnaRadius;
      const z2 = Math.sin(angle + Math.PI) * dnaRadius;

      strand1Vertices.push(x1, y, z1);
      strand2Vertices.push(x2, y, z2);

      // Connect rungs every 6 points
      if (i % 6 === 0) {
        rungsVertices.push(x1, y, z1, x2, y, z2);
      }
    }

    const strand1Geo = new THREE.BufferGeometry();
    strand1Geo.setAttribute('position', new THREE.Float32BufferAttribute(strand1Vertices, 3));
    const strandMat1 = new THREE.PointsMaterial({ size: 0.45, color: 0x38bdf8, transparent: true, opacity: 0.8 });
    const strand1 = new THREE.Points(strand1Geo, strandMat1);
    dnaGroup.add(strand1);

    const strand2Geo = new THREE.BufferGeometry();
    strand2Geo.setAttribute('position', new THREE.Float32BufferAttribute(strand2Vertices, 3));
    const strandMat2 = new THREE.PointsMaterial({ size: 0.45, color: 0x10b981, transparent: true, opacity: 0.8 });
    const strand2 = new THREE.Points(strand2Geo, strandMat2);
    dnaGroup.add(strand2);

    const rungsGeo = new THREE.BufferGeometry();
    rungsGeo.setAttribute('position', new THREE.Float32BufferAttribute(rungsVertices, 3));
    const rungsMat = new THREE.LineBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.35 });
    const rungsLines = new THREE.LineSegments(rungsGeo, rungsMat);
    dnaGroup.add(rungsLines);

    // 5. Starfield / Floating Health Particles
    const starGeo = new THREE.BufferGeometry();
    const starCount = 350;
    const starPos = [];
    for (let i = 0; i < starCount; i++) {
      starPos.push(
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 50
      );
    }
    starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ size: 0.25, color: 0x93c5fd, transparent: true, opacity: 0.4 });
    const starfield = new THREE.Points(starGeo, starMat);
    scene.add(starfield);

    // 6. Mouse Interaction & Parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetRotX = 0;
    let targetRotY = 0;

    const handleMouseMove = (e) => {
      if (!interactive) return;
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      targetRotY = mouseX * 0.6;
      targetRotX = mouseY * 0.4;
    };

    container.addEventListener('mousemove', handleMouseMove);

    // 7. Animation Loop with Systolic Pulse
    const startTime = performance.now();
    let animId;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsedTime = (performance.now() - startTime) / 1000;

      // Pulse calculations (BPM heartbeat rhythm)
      const bps = currentBpm / 60; // beats per sec
      const pulsePhase = (elapsedTime * bps * Math.PI * 2) % (Math.PI * 2);
      
      // Dual-peak heartbeat rhythm (P-wave and strong QRS spike)
      let heartScale = 1.0;
      if (pulsePhase < 0.35) {
        heartScale = 1.0 + Math.sin(pulsePhase * (Math.PI / 0.35)) * 0.16; // Major systole
      } else if (pulsePhase > 0.45 && pulsePhase < 0.75) {
        heartScale = 1.0 + Math.sin((pulsePhase - 0.45) * (Math.PI / 0.3)) * 0.08; // Secondary diastole
      }

      // Smooth camera and rotation damping
      heartGroup.rotation.y += (targetRotY - heartGroup.rotation.y) * 0.05 + 0.005;
      heartGroup.rotation.x += (targetRotX - heartGroup.rotation.x) * 0.05;
      heartGroup.scale.set(heartScale, heartScale, heartScale);

      coreMesh.rotation.y += 0.02;
      coreMesh.rotation.x += 0.01;

      // DNA Rotation
      dnaGroup.rotation.y += 0.008;
      dnaGroup.rotation.x = Math.sin(elapsedTime * 0.5) * 0.15;

      // Background stars gentle sway
      starfield.rotation.y += 0.001;

      // Toggle views visibility based on mode
      if (viewMode === 'heart') {
        heartGroup.visible = true;
        dnaGroup.visible = false;
      } else if (viewMode === 'dna') {
        heartGroup.visible = false;
        dnaGroup.visible = true;
      } else {
        heartGroup.visible = true;
        dnaGroup.visible = true;
      }

      renderer.render(scene, camera);
    };

    animate();

    // 8. Resize Observer
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      container.removeEventListener('mousemove', handleMouseMove);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      heartGeo.dispose();
      heartMat.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      strand1Geo.dispose();
      strand2Geo.dispose();
      rungsGeo.dispose();
      starGeo.dispose();
      renderer.dispose();
    };
  }, [currentBpm, viewMode, interactive]);

  return (
    <div 
      className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-slate-900 via-sky-950 to-slate-900 border border-cyan-500/30 shadow-2xl group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 3D WebGL Canvas Viewport */}
      <div 
        ref={containerRef} 
        style={{ height }} 
        className="w-full cursor-grab active:cursor-grabbing transition"
      />

      {/* Floating 3D Telemetry Overlay */}
      <div className="absolute top-4 left-4 pointer-events-none flex items-center gap-2">
        <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-cyan-500/40 text-white shadow-lg">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="text-xs font-black tracking-wider text-cyan-200">
            {currentBpm} <span className="text-[10px] text-cyan-400 font-semibold">BPM</span>
          </span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        </div>
      </div>

      {/* Mode & Pulse Switcher Controls */}
      {showControls && (
        <div className="absolute bottom-4 inset-x-4 flex items-center justify-between gap-2 pointer-events-auto">
          {/* View Toggles */}
          <div className="flex items-center gap-1 bg-slate-900/80 backdrop-blur-md p-1 rounded-2xl border border-white/10 shadow-lg">
            <button
              onClick={() => setViewMode('heart')}
              className={`px-3 py-1 rounded-xl text-[11px] font-bold transition flex items-center gap-1.5 ${
                viewMode === 'heart' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Heart className="w-3 h-3" />
              <span>3D Heart</span>
            </button>
            <button
              onClick={() => setViewMode('dna')}
              className={`px-3 py-1 rounded-xl text-[11px] font-bold transition flex items-center gap-1.5 ${
                viewMode === 'dna' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Orbit className="w-3 h-3" />
              <span>DNA Helix</span>
            </button>
            <button
              onClick={() => setViewMode('both')}
              className={`px-3 py-1 rounded-xl text-[11px] font-bold transition flex items-center gap-1.5 ${
                viewMode === 'both' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Sparkles className="w-3 h-3" />
              <span>Dual Matrix</span>
            </button>
          </div>

          {/* Quick BPM Pulse Adjuster */}
          <div className="hidden sm:flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-2xl border border-white/10 text-white text-[11px]">
            <span className="text-slate-400 text-[10px] font-bold uppercase">Rate:</span>
            {[60, 72, 85, 110].map((rate) => (
              <button
                key={rate}
                onClick={() => setCurrentBpm(rate)}
                className={`px-2 py-0.5 rounded-lg font-extrabold text-[10px] transition ${
                  currentBpm === rate 
                    ? 'bg-rose-500 text-white' 
                    : 'text-slate-400 hover:text-white hover:bg-white/10'
                }`}
              >
                {rate}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Helper Interaction Hint */}
      <div className={`absolute top-4 right-4 pointer-events-none text-[10px] text-cyan-300/80 bg-slate-950/60 backdrop-blur-sm px-2.5 py-1 rounded-full border border-cyan-500/20 transition-opacity duration-300 ${isHovered ? 'opacity-100' : 'opacity-40'}`}>
        ✨ Drag or move cursor to rotate in 3D
      </div>
    </div>
  );
}
