import React from 'react';
import { Sparkles, Tv, Volume2, VolumeX, ShieldCheck, Gamepad2 } from 'lucide-react';
import { sfx } from '../utils/audio';

export default function Header({ crtEnabled, setCrtEnabled, soundEnabled, setSoundEnabled }) {
  return (
    <header className="border-b border-[#222838] bg-[#12141d]/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        
        {/* Logo / Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-gradient-to-br from-[#00e5ff] via-[#651fff] to-[#ff0077] p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-[#0c0d12] rounded flex items-center justify-center">
              <Gamepad2 className="w-5 h-5 text-[#00e5ff]" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-pixel text-xl tracking-wider text-white font-bold">
                RETROMORPH <span className="text-[#00e5ff]">AI</span>
              </h1>
              <span className="text-[10px] bg-[#1d2333] text-[#00e5ff] px-2 py-0.5 rounded font-mono border border-cyan-500/30">
                PS1 ENGINE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              One Photo. Game-Ready Retro 3D Character Asset.
            </p>
          </div>
        </div>

        {/* Action Toggles */}
        <div className="flex items-center space-x-2">
          {/* CRT toggle */}
          <button
            onClick={() => {
              sfx.playClick();
              setCrtEnabled(!crtEnabled);
            }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-mono border transition ${
              crtEnabled
                ? 'bg-cyan-950/60 text-[#00e5ff] border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                : 'bg-[#181b26] text-slate-400 border-slate-700/50 hover:text-white'
            }`}
            title="Toggle CRT Scanline Simulation"
          >
            <Tv className="w-3.5 h-3.5" />
            <span>CRT: {crtEnabled ? 'ON' : 'OFF'}</span>
          </button>

          {/* Sound toggle */}
          <button
            onClick={() => {
              const next = !soundEnabled;
              setSoundEnabled(next);
              sfx.muted = !next;
              if (next) sfx.playClick();
            }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-mono border transition ${
              soundEnabled
                ? 'bg-purple-950/60 text-purple-300 border-purple-500/40'
                : 'bg-[#181b26] text-slate-500 border-slate-700/50'
            }`}
            title="Toggle Retro Sound Effects"
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-purple-400" /> : <VolumeX className="w-3.5 h-3.5" />}
            <span>SFX</span>
          </button>
        </div>

      </div>
    </header>
  );
}
