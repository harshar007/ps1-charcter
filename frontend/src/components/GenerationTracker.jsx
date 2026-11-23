import React from 'react';
import { Loader2, CheckCircle, AlertCircle, Cpu, Image, Box, Terminal } from 'lucide-react';

const STAGES = [
  { id: 'quality', label: 'ML Readiness', min: 15, icon: Cpu },
  { id: 'concept', label: '2D Concept', min: 40, icon: Image },
  { id: 'geometry', label: '3D Geometry', min: 65, icon: Box },
  { id: 'blender', label: 'Blender Decimation', min: 85, icon: Terminal },
  { id: 'complete', label: 'GLB Ready', min: 100, icon: CheckCircle },
];

export default function GenerationTracker({ jobData }) {
  if (!jobData) return null;

  const { progress = 0, current_stage = 'Processing...', status, error } = jobData;
  const isFailed = status === 'failed';
  const isCompleted = status === 'completed';

  return (
    <div className="bg-[#141722] border border-[#262b3d] rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {!isCompleted && !isFailed ? (
            <Loader2 className="w-4 h-4 text-[#00e5ff] animate-spin" />
          ) : isFailed ? (
            <AlertCircle className="w-4 h-4 text-rose-500" />
          ) : (
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          )}
          <span className="font-mono text-sm font-bold text-white uppercase tracking-wider">
            Pipeline Progress: {progress}%
          </span>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-black/40 px-2 py-0.5 rounded border border-white/5">
          STATUS: {status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-[#0a0b10] rounded-full h-2.5 overflow-hidden border border-slate-800">
        <div
          className={`h-full transition-all duration-500 ${
            isFailed
              ? 'bg-rose-500'
              : 'bg-gradient-to-r from-[#00e5ff] via-[#651fff] to-[#ff0077]'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Stage Icons */}
      <div className="grid grid-cols-5 gap-1 pt-1">
        {STAGES.map((s, idx) => {
          const reached = progress >= s.min;
          const Icon = s.icon;
          return (
            <div
              key={s.id}
              className={`flex flex-col items-center text-center p-1.5 rounded transition ${
                reached ? 'text-[#00e5ff]' : 'text-slate-600'
              }`}
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center mb-1 text-xs border ${
                  reached
                    ? 'border-cyan-500/50 bg-cyan-950/40 text-cyan-300'
                    : 'border-slate-800 bg-[#0c0d12] text-slate-600'
                }`}
              >
                <Icon className="w-3 h-3" />
              </div>
              <span className="text-[9px] font-mono leading-tight">{s.label}</span>
            </div>
          );
        })}
      </div>

      {/* Stage Message Log */}
      <div className="bg-[#0b0d14] rounded-lg p-2.5 border border-slate-800/80 font-mono text-xs flex items-center space-x-2">
        <span className="text-cyan-400">&gt;</span>
        <span className="text-slate-300 truncate">
          {error ? `ERROR: ${error}` : current_stage}
        </span>
      </div>
    </div>
  );
}
