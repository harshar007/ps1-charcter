import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, Info, Activity } from 'lucide-react';

export default function QualityReportCard({ qualityData, isCheckingQuality }) {
  if (isCheckingQuality) {
    return (
      <div className="bg-[#141722] border border-[#262b3d] rounded-xl p-5 shadow-lg animate-pulse">
        <div className="flex items-center space-x-3">
          <Activity className="w-5 h-5 text-[#00e5ff] animate-spin" />
          <div>
            <p className="text-sm font-mono text-white font-medium">
              ML Model analyzing image features...
            </p>
            <p className="text-xs text-slate-400">
              Evaluating blur score, contrast, exposure & subject framing
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!qualityData) {
    return null;
  }

  const { is_ready, confidence, summary, features, diagnostics, suggestions } = qualityData;

  return (
    <div
      className={`rounded-xl p-5 border shadow-lg transition ${
        is_ready
          ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-100'
          : 'bg-amber-950/25 border-amber-500/40 text-amber-100'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2.5">
          {is_ready ? (
            <div className="p-1.5 rounded-full bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : (
            <div className="p-1.5 rounded-full bg-amber-500/20 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          )}
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-mono text-sm font-bold uppercase tracking-wider">
                ML Readiness Assessment: {is_ready ? 'READY' : 'RETAKE SUGGESTED'}
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-black/40 border border-white/10">
                {(confidence * 100).toFixed(1)}% Confidence
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">{summary}</p>
          </div>
        </div>
      </div>

      {/* Feature Metrics Chips */}
      {features && (
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
          <div className="bg-black/30 rounded p-2 border border-white/5">
            <span className="text-[10px] text-slate-400 block">Blur Score (Laplacian)</span>
            <span className={`font-bold ${features.blur_score < 75 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {features.blur_score?.toFixed(1)}
            </span>
          </div>

          <div className="bg-black/30 rounded p-2 border border-white/5">
            <span className="text-[10px] text-slate-400 block">Brightness (0-255)</span>
            <span className="text-white font-bold">{features.brightness_mean?.toFixed(1)}</span>
          </div>

          <div className="bg-black/30 rounded p-2 border border-white/5">
            <span className="text-[10px] text-slate-400 block">RMS Contrast</span>
            <span className="text-white font-bold">{features.contrast_rms?.toFixed(1)}</span>
          </div>

          <div className="bg-black/30 rounded p-2 border border-white/5">
            <span className="text-[10px] text-slate-400 block">Resolution</span>
            <span className="text-white font-bold">
              {features.width}×{features.height}
            </span>
          </div>
        </div>
      )}

      {/* Diagnostic Tips */}
      {suggestions && suggestions.length > 0 && (
        <div className="mt-3 pt-3 border-t border-white/10 text-xs">
          <span className="font-mono text-[11px] uppercase tracking-wider font-semibold text-slate-300 block mb-1">
            Guidance & Recommendations:
          </span>
          <ul className="list-disc list-inside space-y-0.5 text-slate-300">
            {suggestions.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
