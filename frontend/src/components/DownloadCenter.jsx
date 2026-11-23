import React from 'react';
import { Download, Box, Image as ImageIcon, FileText, Palette, CheckCircle2 } from 'lucide-react';
import { sfx } from '../utils/audio';

export default function DownloadCenter({ jobId, jobData }) {
  if (!jobId || !jobData || jobData.status !== 'completed') return null;

  return (
    <div className="bg-[#141722] border border-emerald-500/30 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center space-x-2">
        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        <h2 className="text-sm font-mono uppercase tracking-wider text-white font-bold">
          Export & Game-Ready Asset Downloads
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* 1. Download GLB */}
        <a
          href={`/api/jobs/${jobId}/model`}
          download={`ps1_character_${jobId.slice(0, 8)}.glb`}
          onClick={() => sfx.playSuccess()}
          className="flex items-center space-x-3 p-3 bg-gradient-to-r from-cyan-950/60 to-blue-950/60 hover:from-cyan-900/80 hover:to-blue-900/80 border border-cyan-500/40 rounded-lg text-white transition group"
        >
          <div className="p-2 bg-cyan-500/20 text-[#00e5ff] rounded group-hover:scale-105 transition">
            <Box className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <span className="text-xs font-mono font-bold block truncate">Download 3D GLB</span>
            <span className="text-[10px] text-slate-300">Unity • Unreal • Godot</span>
          </div>
        </a>

        {/* 2. Download Concept Art */}
        <a
          href={`/api/jobs/${jobId}/preview`}
          download={`ps1_concept_${jobId.slice(0, 8)}.png`}
          onClick={() => sfx.playSuccess()}
          className="flex items-center space-x-3 p-3 bg-gradient-to-r from-purple-950/60 to-pink-950/60 hover:from-purple-900/80 hover:to-pink-900/80 border border-purple-500/40 rounded-lg text-white transition group"
        >
          <div className="p-2 bg-purple-500/20 text-purple-300 rounded group-hover:scale-105 transition">
            <ImageIcon className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <span className="text-xs font-mono font-bold block truncate">2D Concept Card</span>
            <span className="text-[10px] text-slate-300">PS1 Dithered Art (PNG)</span>
          </div>
        </a>

        {/* 3. Download Retro Texture */}
        <a
          href={`/api/jobs/${jobId}/texture`}
          download={`retro_texture_${jobId.slice(0, 8)}.png`}
          onClick={() => sfx.playSuccess()}
          className="flex items-center space-x-3 p-3 bg-[#10121a] hover:bg-[#181b26] border border-slate-700/60 rounded-lg text-white transition group"
        >
          <div className="p-2 bg-slate-800 text-amber-400 rounded group-hover:scale-105 transition">
            <Palette className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <span className="text-xs font-mono font-bold block truncate">UV Texture Atlas</span>
            <span className="text-[10px] text-slate-400">Baked Nearest-Neighbor</span>
          </div>
        </a>

        {/* 4. Download ML Report */}
        <a
          href={`/api/jobs/${jobId}/report`}
          download={`metadata_report_${jobId.slice(0, 8)}.json`}
          onClick={() => sfx.playSuccess()}
          className="flex items-center space-x-3 p-3 bg-[#10121a] hover:bg-[#181b26] border border-slate-700/60 rounded-lg text-white transition group"
        >
          <div className="p-2 bg-slate-800 text-slate-300 rounded group-hover:scale-105 transition">
            <FileText className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <span className="text-xs font-mono font-bold block truncate">ML Quality Report</span>
            <span className="text-[10px] text-slate-400">JSON Diagnostics</span>
          </div>
        </a>
      </div>
    </div>
  );
}
