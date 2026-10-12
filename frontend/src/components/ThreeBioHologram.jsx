import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Activity, ShieldCheck, HeartPulse, Sparkles, Thermometer, Radio, Eye } from 'lucide-react';

export default function ThreeBioHologram({ 
  heartRate = 68, 
  systolic = 118, 
  diastolic = 76, 
  glucose = 89, 
  temperature = 98.6
}) {
  const mountRef = useRef(null);
  const cardRef = useRef(null);
  const [viewMode, setViewMode] = useState('wireframe'); // default to 'wireframe' matching screenshot
  const [activeBeacon, setActiveBeacon] = useState(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  // 3D Mouse Parallax Tilt for the Medical Suite
  const handleMouseMove = (e) => {
    if (!cardRef.current || viewMode !== 'suite') return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: x * 14, y: -y * 14 });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setActiveBeacon(null);
  };

  // Three.js Wireframe Canvas (active in wireframe mode or as ambient backdrop)
  useEffect(() => {
    if (viewMode !== 'wireframe') return;
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth || 300;
    const height = mount.clientHeight || 200;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.z = 18;

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      mount.innerHTML = '';
      mount.appendChild(renderer.domElement);
    } catch (e) {
      console.warn('WebGL initialization skipped for hologram:', e);
      return;
    }

    const hologramGroup = new THREE.Group();
    scene.add(hologramGroup);

    // 1. Concentric Holographic Tech Rings
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x06b6d4, wireframe: true, transparent: true, opacity: 0.5 });
    const ringGeo1 = new THREE.TorusGeometry(6, 0.08, 16, 60);
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    hologramGroup.add(ring1);

    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.4 });
    const ringGeo2 = new THREE.TorusGeometry(4.8, 0.06, 16, 60);
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.x = Math.PI / 3;
    hologramGroup.add(ring2);

    const ringMat3 = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.35 });
    const ringGeo3 = new THREE.TorusGeometry(3.5, 0.05, 16, 50);
    const ring3 = new THREE.Mesh(ringGeo3, ringMat3);
    ring3.rotation.y = Math.PI / 4;
    hologramGroup.add(ring3);

    // 2. Central Icosahedron Biomarker Core
    const coreGeo = new THREE.IcosahedronGeometry(2.2, 1);
    const coreMat = new THREE.MeshBasicMaterial({ 
      color: 0x0284c7, 
      wireframe: true, 
      transparent: true, 
      opacity: 0.65,
      blending: THREE.AdditiveBlending 
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    hologramGroup.add(core);

    // 3. Floating Data Particles around sphere
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const particlePos = [];
    for (let i = 0; i < particleCount; i++) {
      const radius = 6.5 + Math.random() * 2.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      particlePos.push(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi)
      );
    }
    particleGeo.setAttribute('position', new THREE.Float32BufferAttribute(particlePos, 3));
    const particleMat = new THREE.PointsMaterial({ size: 0.35, color: 0x22d3ee, transparent: true, opacity: 0.8 });
    const particles = new THREE.Points(particleGeo, particleMat);
    hologramGroup.add(particles);

    // Animation loop
    let animId;
    const startTime = performance.now();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const time = (performance.now() - startTime) / 1000;

      ring1.rotation.z += 0.01;
      ring1.rotation.y += 0.005;

      ring2.rotation.z -= 0.012;
      ring2.rotation.x += 0.008;

      ring3.rotation.y += 0.015;

      core.rotation.x += 0.007;
      core.rotation.y += 0.009;

      particles.rotation.y += 0.003;

      const pulse = 1.0 + Math.sin(time * 3) * 0.05;
      core.scale.set(pulse, pulse, pulse);

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!mount) return;
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (mount.contains(renderer.domElement)) {
        mount.removeChild(renderer.domElement);
      }
      ringGeo1.dispose();
      ringMat1.dispose();
      ringGeo2.dispose();
      ringMat2.dispose();
      ringGeo3.dispose();
      ringMat3.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      renderer.dispose();
    };
  }, [viewMode]);

  const beacons = [
    {
      id: 'heart',
      name: '3D Heart & ECG',
      reading: `${heartRate} BPM`,
      desc: 'Real-time cardiac pulse rhythm',
      position: { left: '14%', top: '56%' },
      color: 'from-rose-500 to-pink-500',
      badgeColor: 'border-rose-400 text-rose-300'
    },
    {
      id: 'bp',
      name: 'Blood Pressure Monitor',
      reading: `${systolic}/${diastolic} mmHg`,
      desc: 'Systolic / Diastolic arterial pressure',
      position: { left: '36%', top: '64%' },
      color: 'from-cyan-500 to-blue-500',
      badgeColor: 'border-cyan-400 text-cyan-300'
    },
    {
      id: 'avatar',
      name: 'Holographic Scanner',
      reading: 'Biometric Sync Active',
      desc: 'Full-body physiological telemetry',
      position: { left: '50%', top: '30%' },
      color: 'from-teal-400 to-emerald-500',
      badgeColor: 'border-teal-400 text-teal-300'
    },
    {
      id: 'oximeter',
      name: 'Pulse Oximeter',
      reading: '99% SpO2',
      desc: 'Capillary blood oxygen saturation',
      position: { left: '65%', top: '64%' },
      color: 'from-red-500 to-rose-600',
      badgeColor: 'border-red-400 text-rose-300'
    },
    {
      id: 'temp',
      name: 'Clinical Thermometer',
      reading: `${temperature}°F`,
      desc: 'Core body temperature telemetry',
      position: { left: '88%', top: '58%' },
      color: 'from-amber-400 to-orange-500',
      badgeColor: 'border-amber-400 text-amber-300'
    }
  ];

  return (
    <div 
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative bg-gradient-to-br from-slate-950 via-slate-900 to-sky-950 rounded-3xl p-5 border border-cyan-500/30 text-white shadow-2xl overflow-hidden transition-all duration-200"
    >
      {/* Top Header matching screenshot */}
      <div className="flex items-center justify-between mb-2 relative z-20">
        <div className="flex items-center gap-2">
          <HeartPulse className="w-4 h-4 text-cyan-400 animate-pulse" />
          <h3 className="text-xs font-black uppercase tracking-wider text-cyan-200">
            3D Biometric Hologram
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-slate-900/90 border border-white/10 rounded-xl p-0.5 flex items-center text-[10px]">
            <button
              onClick={() => setViewMode('wireframe')}
              className={`px-2 py-0.5 rounded-lg font-bold transition ${
                viewMode === 'wireframe' 
                  ? 'bg-cyan-500 text-slate-950 shadow-sm' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              🌐 Hologram
            </button>
            <button
              onClick={() => setViewMode('suite')}
              className={`px-2 py-0.5 rounded-lg font-bold transition ${
                viewMode === 'suite' 
                  ? 'bg-cyan-500 text-slate-950 shadow-sm' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              ✨ Suite
            </button>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            Live Sync
          </span>
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'suite' ? (
        <div className="relative w-full overflow-hidden rounded-2xl border border-cyan-500/20 bg-slate-950/80 shadow-inner group">
          {/* 3D Holographic Scene Image with Dynamic Tilt */}
          <div 
            style={{
              transform: `perspective(1000px) rotateY(${tilt.x}deg) rotateX(${tilt.y}deg) scale3d(1.02, 1.02, 1.02)`,
              transition: 'transform 0.15s ease-out'
            }}
            className="relative w-full h-56 sm:h-64 flex items-center justify-center overflow-hidden"
          >
            <img 
              src="/3d_biometric_suite.png" 
              alt="3D Biometric Medical Telemetry Suite"
              className="w-full h-full object-cover object-center filter brightness-105 contrast-110 drop-shadow-[0_10px_20px_rgba(6,182,212,0.3)]"
            />

            {/* Glowing Ambient Radial Vignette */}
            <div className="absolute inset-0 bg-radial-gradient from-transparent via-cyan-950/10 to-slate-950/70 pointer-events-none" />

            {/* Interactive Sensor Hotspot Beacons */}
            {beacons.map((beacon) => {
              const isSelected = activeBeacon?.id === beacon.id;
              return (
                <div 
                  key={beacon.id}
                  style={{ left: beacon.position.left, top: beacon.position.top }}
                  onMouseEnter={() => setActiveBeacon(beacon)}
                  className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer z-30 group/beacon"
                >
                  {/* Ping Ring */}
                  <span className={`absolute -inset-2 rounded-full bg-gradient-to-r ${beacon.color} opacity-40 animate-ping`} />
                  
                  {/* Center Dot Beacon */}
                  <button 
                    onClick={() => setActiveBeacon(beacon)}
                    className={`relative w-4 h-4 rounded-full bg-gradient-to-r ${beacon.color} border-2 border-white shadow-lg flex items-center justify-center transition-transform hover:scale-125 ${
                      isSelected ? 'scale-125 ring-4 ring-cyan-400/50' : ''
                    }`}
                  >
                    <span className="w-1 h-1 rounded-full bg-white" />
                  </button>

                  {/* Hover Floating Mini Tooltip */}
                  <div className="absolute bottom-6 left-1/2 -translate-x-1/2 hidden group-hover/beacon:flex flex-col items-center pointer-events-none whitespace-nowrap z-40 transition-all">
                    <div className="bg-slate-950/95 backdrop-blur-md px-2.5 py-1.5 rounded-xl border border-cyan-400/50 shadow-2xl text-center">
                      <div className="text-[10px] font-extrabold text-cyan-200">{beacon.name}</div>
                      <div className="text-xs font-black text-white">{beacon.reading}</div>
                    </div>
                    <div className="w-2 h-2 bg-slate-950 rotate-45 border-r border-b border-cyan-400/50 -mt-1" />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active Sensor Context Info Card */}
          <div className="absolute bottom-2 inset-x-2 bg-slate-950/85 backdrop-blur-md border border-cyan-500/30 rounded-xl px-3 py-1.5 flex items-center justify-between text-xs transition">
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-bold text-slate-300">
                {activeBeacon ? activeBeacon.name : 'Hover or tap beacons on 3D devices'}
              </span>
            </div>
            <div className="font-extrabold text-cyan-300 text-xs">
              {activeBeacon ? activeBeacon.reading : '5 Sensor Channels Synced'}
            </div>
          </div>
        </div>
      ) : (
        /* Wireframe Three.js Viewport */
        <div ref={mountRef} className="w-full h-60 sm:h-64 cursor-grab rounded-2xl bg-slate-950/80 border border-cyan-500/20" />
      )}

      {/* Overlay Telemetry stats grid matching screenshot */}
      <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-cyan-500/20 text-center">
        <div className="bg-white/5 backdrop-blur-sm p-2 rounded-xl border border-white/5 hover:border-rose-500/30 transition">
          <div className="text-[10px] text-slate-400 font-semibold">Pulse</div>
          <div className="text-sm font-black text-rose-400">{heartRate} <span className="text-[9px] font-normal">bpm</span></div>
        </div>

        <div className="bg-white/5 backdrop-blur-sm p-2 rounded-xl border border-white/5 hover:border-cyan-500/30 transition">
          <div className="text-[10px] text-slate-400 font-semibold">BP Target</div>
          <div className="text-sm font-black text-cyan-300">{systolic}/{diastolic}</div>
        </div>

        <div className="bg-white/5 backdrop-blur-sm p-2 rounded-xl border border-white/5 hover:border-emerald-500/30 transition">
          <div className="text-[10px] text-slate-400 font-semibold">Glucose</div>
          <div className="text-sm font-black text-emerald-300">{glucose} <span className="text-[9px] font-normal">mg/dL</span></div>
        </div>
      </div>
    </div>
  );
}
