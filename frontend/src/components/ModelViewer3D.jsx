import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Eye, RotateCw, Box, Grid, RefreshCw, Image as ImageIcon, Layers } from 'lucide-react';
import { sfx } from '../utils/audio';

export default function ModelViewer3D({ modelUrl, previewUrl, jobId }) {
  const containerRef = useRef(null);
  const [activeTab, setActiveTab] = useState('3d'); // '3d' or 'concept'
  const [wireframe, setWireframe] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [polyStats, setPolyStats] = useState({ vertices: 0, triangles: 0 });
  const [isLoading, setIsLoading] = useState(true);

  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const currentModelRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !modelUrl) return;

    // Setup Three.js scene
    const container = containerRef.current;
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 450;

    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0x0c0e15);

    // Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.3, 3.2);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1.0, 0);
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 2.0;
    controlsRef.current = controls;

    // Lighting (PS1 retro stage lighting: ambient + directional fill)
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.4);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xfff5e6, 2.0);
    dirLight1.position.set(2, 4, 3);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x70a0ff, 1.0);
    dirLight2.position.set(-2, 2, -2);
    scene.add(dirLight2);

    // PS1 style floor grid
    const gridHelper = new THREE.GridHelper(4, 16, 0x00e5ff, 0x222a3a);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Load GLTF / GLB model
    setIsLoading(true);
    const loader = new GLTFLoader();
    loader.load(
      modelUrl,
      (gltf) => {
        let verts = 0;
        let tris = 0;

        gltf.scene.traverse((child) => {
          if (child.isMesh) {
            // Count geometry
            if (child.geometry) {
              const geom = child.geometry;
              verts += geom.attributes.position ? geom.attributes.position.count : 0;
              tris += geom.index ? geom.index.count / 3 : geom.attributes.position.count / 3;
            }

            // Apply nearest neighbor pixel filter on all textures for authentic PS1 look
            if (child.material) {
              const materials = Array.isArray(child.material) ? child.material : [child.material];
              materials.forEach((mat) => {
                if (mat.map) {
                  mat.map.magFilter = THREE.NearestFilter;
                  mat.map.minFilter = THREE.NearestFilter;
                  mat.map.needsUpdate = true;
                }
                mat.wireframe = wireframe;
              });
            }
          }
        });

        setPolyStats({ vertices: verts, triangles: Math.round(tris) });
        currentModelRef.current = gltf.scene;
        scene.add(gltf.scene);
        setIsLoading(false);
      },
      undefined,
      (err) => {
        console.error('Error loading 3D model:', err);
        setIsLoading(false);
      }
    );

    // Animation Loop
    let animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      renderer.render(scene, camera);
    };
    animate();

    // Handle Resize
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
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [modelUrl]);

  // Update wireframe mode
  useEffect(() => {
    if (!currentModelRef.current) return;
    currentModelRef.current.traverse((child) => {
      if (child.isMesh && child.material) {
        const materials = Array.isArray(child.material) ? child.material : [child.material];
        materials.forEach((m) => {
          m.wireframe = wireframe;
        });
      }
    });
  }, [wireframe]);

  // Update auto-rotate
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate;
    }
  }, [autoRotate]);

  const resetCamera = () => {
    sfx.playClick();
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(0, 1.3, 3.2);
      controlsRef.current.target.set(0, 1.0, 0);
      controlsRef.current.update();
    }
  };

  return (
    <div className="bg-[#141722] border border-[#262b3d] rounded-xl overflow-hidden shadow-2xl flex flex-col">
      {/* Top Bar with Mode Tabs */}
      <div className="bg-[#10121a] px-4 py-3 border-b border-[#222838] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              sfx.playClick();
              setActiveTab('3d');
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center space-x-1.5 transition ${
              activeTab === '3d'
                ? 'bg-cyan-950/80 text-[#00e5ff] border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Box className="w-3.5 h-3.5" />
            <span>3D GLB Viewport</span>
          </button>

          {previewUrl && (
            <button
              onClick={() => {
                sfx.playClick();
                setActiveTab('concept');
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center space-x-1.5 transition ${
                activeTab === 'concept'
                  ? 'bg-purple-950/80 text-purple-300 border border-purple-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>2D PS1 Concept Card</span>
            </button>
          )}
        </div>

        {/* Polygon / Geometry Stats */}
        {activeTab === '3d' && (
          <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
            <span>
              Triangles: <strong className="text-white">{polyStats.triangles}</strong>
            </span>
            <span>
              Vertices: <strong className="text-white">{polyStats.vertices}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Main View Area */}
      <div className="relative w-full h-[460px] bg-[#0c0e15]">
        {/* 3D Canvas */}
        <div
          ref={containerRef}
          className={`w-full h-full ${activeTab === '3d' ? 'block' : 'hidden'}`}
        />

        {/* 2D Concept Image Card */}
        {activeTab === 'concept' && previewUrl && (
          <div className="w-full h-full flex items-center justify-center p-4 bg-[#08090d]">
            <img
              src={previewUrl}
              alt="PS1 Concept Art"
              className="max-h-full max-w-full object-contain rounded border border-cyan-500/30 shadow-2xl"
            />
          </div>
        )}

        {/* Viewport Overlay Controls (when in 3D mode) */}
        {activeTab === '3d' && (
          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between pointer-events-none">
            <div className="flex items-center space-x-1.5 pointer-events-auto bg-black/70 backdrop-blur px-2.5 py-1.5 rounded-lg border border-white/10 text-xs font-mono">
              {/* Wireframe toggle */}
              <button
                onClick={() => {
                  sfx.playClick();
                  setWireframe(!wireframe);
                }}
                className={`p-1.5 rounded hover:bg-white/10 transition ${
                  wireframe ? 'text-[#00e5ff] font-bold' : 'text-slate-400'
                }`}
                title="Toggle Polygonal Wireframe"
              >
                <Layers className="w-4 h-4" />
              </button>

              {/* Auto rotate toggle */}
              <button
                onClick={() => {
                  sfx.playClick();
                  setAutoRotate(!autoRotate);
                }}
                className={`p-1.5 rounded hover:bg-white/10 transition ${
                  autoRotate ? 'text-[#00e5ff]' : 'text-slate-400'
                }`}
                title="Toggle Turntable Rotation"
              >
                <RotateCw className="w-4 h-4" />
              </button>

              {/* Reset camera */}
              <button
                onClick={resetCamera}
                className="p-1.5 rounded hover:bg-white/10 text-slate-400 hover:text-white transition"
                title="Reset View"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            <div className="pointer-events-none font-mono text-[10px] text-slate-400 bg-black/60 px-2 py-1 rounded border border-white/5">
              Drag to Orbit • Scroll to Zoom
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
