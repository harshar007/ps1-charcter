import React, { useState, useEffect, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Sparkles, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { sfx } from '../utils/audio';

export default function PhotoUpload({
  selectedFile,
  setSelectedFile,
  previewUrl,
  setPreviewUrl,
  qualityData,
  setQualityData,
  isCheckingQuality,
  setIsCheckingQuality
}) {
  const [samples, setSamples] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Load sample presets from backend
  useEffect(() => {
    fetch('/api/samples')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.samples) {
          setSamples(data.samples);
        }
      })
      .catch((err) => console.log('Samples not loaded:', err));
  }, []);

  const runQualityCheck = async (file) => {
    setIsCheckingQuality(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      const res = await fetch('/api/check-quality', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setQualityData(data);
        if (data.is_ready) {
          sfx.playSuccess();
        } else {
          sfx.playError();
        }
      }
    } catch (err) {
      console.error('Quality check error:', err);
    } finally {
      setIsCheckingQuality(false);
    }
  };

  const handleFileChange = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    sfx.playClick();
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    runQualityCheck(file);
  };

  const handleSampleClick = async (sample) => {
    sfx.playClick();
    try {
      const res = await fetch(sample.url);
      const blob = await res.blob();
      const file = new File([blob], sample.filename, { type: 'image/jpeg' });
      handleFileChange(file);
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  };

  return (
    <div className="bg-[#141722] border border-[#262b3d] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-mono uppercase tracking-wider text-white flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-[#00e5ff] inline-block"></span>
          <span>1. Upload Photograph</span>
        </h2>
        {selectedFile && (
          <button
            onClick={() => {
              sfx.playClick();
              setSelectedFile(null);
              setPreviewUrl(null);
              setQualityData(null);
            }}
            className="text-xs text-slate-400 hover:text-rose-400 flex items-center space-x-1"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileChange(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
          isDragging
            ? 'border-[#00e5ff] bg-cyan-950/20'
            : previewUrl
            ? 'border-cyan-500/30 bg-[#10121a]'
            : 'border-slate-700/60 hover:border-slate-500 bg-[#0f1118]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileChange(e.target.files[0]);
            }
          }}
        />

        {previewUrl ? (
          <div className="flex flex-col items-center">
            <div className="relative group">
              <img
                src={previewUrl}
                alt="Source reference"
                className="w-36 h-36 object-cover rounded-lg border border-slate-700 shadow-md group-hover:opacity-80 transition"
              />
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition bg-black/50 rounded-lg">
                <span className="text-xs text-white font-mono bg-black/80 px-2 py-1 rounded">
                  Change Photo
                </span>
              </div>
            </div>
            <p className="mt-2 text-xs text-slate-300 font-mono font-medium truncate max-w-[200px]">
              {selectedFile?.name}
            </p>
            <p className="text-[11px] text-slate-400">
              {(selectedFile?.size / 1024).toFixed(1)} KB • Image Loaded
            </p>
          </div>
        ) : (
          <div className="py-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-[#1b2030] flex items-center justify-center text-[#00e5ff] mb-3">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-medium text-white mb-1">
              Drag & Drop your photograph here
            </p>
            <p className="text-xs text-slate-400 mb-2">
              Supports JPG, PNG, WEBP (Full-body or portrait)
            </p>
            <span className="inline-block px-3 py-1 bg-[#1e2334] text-xs font-mono text-cyan-400 rounded border border-cyan-500/20">
              Browse from device
            </span>
          </div>
        )}
      </div>

      {/* Instant Presets / Samples */}
      {samples.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-mono text-slate-400 mb-2 flex items-center space-x-1">
            <Sparkles className="w-3 h-3 text-[#00e5ff]" />
            <span>Or try ready-made reference samples:</span>
          </p>
          <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
            {samples.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSampleClick(s)}
                className="group relative rounded overflow-hidden border border-slate-800 hover:border-cyan-400 transition focus:outline-none"
                title={`${s.title} (${s.expected_label.toUpperCase()})`}
              >
                <img
                  src={s.url}
                  alt={s.title}
                  className="w-full h-14 object-cover group-hover:scale-105 transition"
                />
                <span
                  className={`absolute bottom-0 inset-x-0 text-[9px] font-mono text-center py-0.5 truncate ${
                    s.expected_label === 'ready'
                      ? 'bg-emerald-950/90 text-emerald-300'
                      : 'bg-amber-950/90 text-amber-300'
                  }`}
                >
                  {s.expected_label}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
