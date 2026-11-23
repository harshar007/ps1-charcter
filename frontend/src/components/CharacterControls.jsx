import React from 'react';
import { User, Sparkles, Layers, Sliders, Box, Cpu, Zap } from 'lucide-react';
import { sfx } from '../utils/audio';

const GENDER_OPTIONS = [
  { id: 'male', label: 'Male', icon: '♂' },
  { id: 'female', label: 'Female', icon: '♀' },
  { id: 'custom', label: 'Custom / Non-Binary', icon: '✦' },
];

const OUTFIT_OPTIONS = [
  { id: 'casual', label: 'Casual', desc: 'Faded denim & vintage tee' },
  { id: 'formal', label: 'Formal', desc: 'Noir charcoal suit & tie' },
  { id: 'police', label: 'Police', desc: 'R.P.D. patrol uniform & cap' },
  { id: 'horror', label: 'Horror', desc: 'Weathered survivor coat' },
  { id: 'traditional', label: 'Traditional', desc: 'Ceremonial martial robes' },
  { id: 'custom', label: 'Custom', desc: 'User-specified prompt' },
];

const POLYGON_LEVELS = [
  { id: 'low', label: 'Low', desc: '~1,200 Triangles (FF7 / Tomb Raider 1)' },
  { id: 'medium', label: 'Medium', desc: '~2,500 Triangles (Resident Evil 2 / MGS1)' },
  { id: 'high', label: 'High', desc: '~5,000 Triangles (Silent Hill / Tekken 3)' },
];

const TEXTURE_SIZES = [
  { id: 64, label: '64×64', desc: 'Ultra Retro Pixelated' },
  { id: 128, label: '128×128', desc: 'Authentic PS1 VRAM Standard' },
  { id: 256, label: '256×256', desc: 'High-Res Late PS1 Style' },
];

export default function CharacterControls({
  gender,
  setGender,
  outfit,
  setOutfit,
  customOutfit,
  setCustomOutfit,
  polyLevel,
  setPolyLevel,
  textureSize,
  setTextureSize,
  pose,
  setPose,
  affineJitter,
  setAffineJitter,
  onGenerate,
  isGenerating,
  canGenerate
}) {
  return (
    <div className="bg-[#141722] border border-[#262b3d] rounded-xl p-5 shadow-lg space-y-5">
      
      {/* 2. Gender Presentation */}
      <div>
        <h2 className="text-sm font-mono uppercase tracking-wider text-white flex items-center space-x-2 mb-2.5">
          <span className="w-2 h-2 rounded-full bg-[#00e5ff] inline-block"></span>
          <span>2. Gender Presentation</span>
        </h2>
        <div className="grid grid-cols-3 gap-2">
          {GENDER_OPTIONS.map((g) => {
            const active = gender === g.id;
            return (
              <button
                key={g.id}
                type="button"
                onClick={() => {
                  sfx.playClick();
                  setGender(g.id);
                }}
                className={`py-2 px-3 rounded-lg border text-xs font-mono flex items-center justify-center space-x-1.5 transition ${
                  active
                    ? 'bg-cyan-950/70 border-[#00e5ff] text-cyan-300 font-bold shadow-sm shadow-cyan-500/20'
                    : 'bg-[#0f1118] border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                }`}
              >
                <span>{g.icon}</span>
                <span>{g.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Outfit Selection */}
      <div>
        <h2 className="text-sm font-mono uppercase tracking-wider text-white flex items-center space-x-2 mb-2.5">
          <span className="w-2 h-2 rounded-full bg-[#00e5ff] inline-block"></span>
          <span>3. Character Outfit</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {OUTFIT_OPTIONS.map((o) => {
            const active = outfit === o.id;
            return (
              <button
                key={o.id}
                type="button"
                onClick={() => {
                  sfx.playClick();
                  setOutfit(o.id);
                }}
                className={`p-2.5 rounded-lg border text-left transition flex flex-col justify-between ${
                  active
                    ? 'bg-purple-950/60 border-purple-500 text-purple-200 shadow-sm shadow-purple-500/20'
                    : 'bg-[#0f1118] border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                }`}
              >
                <span className="text-xs font-mono font-bold">{o.label}</span>
                <span className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{o.desc}</span>
              </button>
            );
          })}
        </div>

        {outfit === 'custom' && (
          <div className="mt-2.5">
            <input
              type="text"
              value={customOutfit}
              onChange={(e) => setCustomOutfit(e.target.value)}
              placeholder="e.g. Cyberpunk trenchcoat with glowing cyan goggles"
              className="w-full bg-[#0f1118] border border-purple-500/50 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400"
            />
          </div>
        )}
      </div>

      {/* 4. Output Settings */}
      <div className="pt-2 border-t border-slate-800/80">
        <h2 className="text-sm font-mono uppercase tracking-wider text-white flex items-center space-x-2 mb-3">
          <span className="w-2 h-2 rounded-full bg-[#00e5ff] inline-block"></span>
          <span>4. Retro Engine Settings</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Polygon Level */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Polygon Budget:
            </label>
            <select
              value={polyLevel}
              onChange={(e) => {
                sfx.playClick();
                setPolyLevel(e.target.value);
              }}
              className="w-full bg-[#0f1118] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono focus:border-cyan-500"
            >
              {POLYGON_LEVELS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} ({p.desc.split(' ')[0]})
                </option>
              ))}
            </select>
          </div>

          {/* Texture Size */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Texture VRAM Resolution:
            </label>
            <select
              value={textureSize}
              onChange={(e) => {
                sfx.playClick();
                setTextureSize(Number(e.target.value));
              }}
              className="w-full bg-[#0f1118] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono focus:border-cyan-500"
            >
              {TEXTURE_SIZES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Pose */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Export Pose:
            </label>
            <select
              value={pose}
              onChange={(e) => {
                sfx.playClick();
                setPose(e.target.value);
              }}
              className="w-full bg-[#0f1118] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono focus:border-cyan-500"
            >
              <option value="standing">Neutral Standing</option>
              <option value="t_pose">T-Pose (Rigging Ready)</option>
            </select>
          </div>
        </div>

        {/* Affine Jitter toggle */}
        <div className="mt-3 flex items-center justify-between bg-[#0f1118] p-2.5 rounded-lg border border-slate-800/80">
          <div>
            <span className="text-xs font-mono font-medium text-white block">
              PS1 Fixed-Point Vertex Wobble
            </span>
            <span className="text-[10px] text-slate-400">
              Quantizes vertices to grid simulating lack of sub-pixel precision
            </span>
          </div>
          <button
            type="button"
            onClick={() => {
              sfx.playClick();
              setAffineJitter(!affineJitter);
            }}
            className={`w-10 h-5 rounded-full p-0.5 transition ${
              affineJitter ? 'bg-[#00e5ff]' : 'bg-slate-700'
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-black transition transform ${
                affineJitter ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Generate Button */}
      <button
        type="button"
        disabled={!canGenerate || isGenerating}
        onClick={onGenerate}
        className={`w-full py-3.5 px-6 rounded-lg font-mono text-sm uppercase tracking-wider font-bold transition flex items-center justify-center space-x-2 shadow-lg ${
          !canGenerate || isGenerating
            ? 'bg-slate-800/60 text-slate-500 cursor-not-allowed border border-slate-700/40'
            : 'bg-gradient-to-r from-[#00e5ff] via-[#651fff] to-[#ff0077] hover:opacity-95 text-white shadow-cyan-500/25 cursor-pointer transform hover:-translate-y-0.5'
        }`}
      >
        <Zap className="w-4 h-4" />
        <span>{isGenerating ? 'Synthesizing Character Asset...' : 'Generate PS1 Character'}</span>
      </button>

    </div>
  );
}
