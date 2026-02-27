"use client";

import { useEffect, useState } from "react";
import { getConfigStatus, ConfigStatus } from "@/lib/api";

export function StatusBar() {
  const [config, setConfig] = useState<ConfigStatus | null>(null);

  useEffect(() => {
    getConfigStatus().then(setConfig).catch(() => null);
  }, []);

  if (!config) return null;

  return (
    <footer className="border-t border-white/[0.06] px-6 py-3 flex items-center gap-4 text-xs text-white/30">
      <span>API Status:</span>

      <StatusDot label="Claude" active={config.has_claude} />
      <StatusDot label="ElevenLabs" active={config.has_elevenlabs} />
      <StatusDot label="Spotify" active={config.has_spotify} />

      <span className="ml-auto">
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-white/60 transition-colors"
        >
          API Docs ↗
        </a>
      </span>
    </footer>
  );
}

function StatusDot({ label, active }: { label: string; active: boolean }) {
  return (
    <span className="flex items-center gap-1.5">
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          active ? "bg-emerald-400" : "bg-white/20"
        }`}
      />
      {label}
    </span>
  );
}
