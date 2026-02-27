"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { FeedItem, getFeed } from "@/lib/api";

const DENSITY_COLOR: Record<string, string> = {
  "Ultra High": "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
  High: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  Medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function FeedPlayer() {
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeId, setActiveId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    getFeed()
      .then(setFeed)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handlePlay = (item: FeedItem) => {
    if (!item.audio_url) return;
    setActiveId(item.id);
    if (audioRef.current) {
      audioRef.current.src = `http://localhost:8000${item.audio_url}`;
      audioRef.current.play();
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="glass rounded-2xl p-5 animate-pulse">
            <div className="h-4 bg-white/5 rounded w-3/4 mb-3" />
            <div className="h-3 bg-white/5 rounded w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (!feed.length) {
    return (
      <div className="text-center py-20 text-white/40">
        <div className="text-4xl mb-4">🎙️</div>
        <p className="text-lg font-medium text-white/60">Your feed is empty</p>
        <p className="text-sm mt-1">Submit a podcast URL to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <audio ref={audioRef} className="hidden" controls />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Knowledge Feed</h2>
        <span className="text-sm text-white/40">{feed.length} insights</span>
      </div>

      {feed.map((item, idx) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className={`glass rounded-2xl p-5 cursor-pointer transition-all hover:border-white/[0.12] ${
            activeId === item.id ? "border-indigo-500/30 glow-accent" : ""
          }`}
          onClick={() => handlePlay(item)}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm leading-snug mb-1 truncate">
                {item.title}
              </p>
              <p className="text-xs text-white/40 truncate">{item.source}</p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {item.knowledge_density && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                    DENSITY_COLOR[item.knowledge_density] ??
                    "text-white/50 bg-white/5 border-white/10"
                  }`}
                >
                  {item.knowledge_density}
                </span>
              )}
              {item.duration > 0 && (
                <span className="text-xs text-white/30">
                  {formatDuration(item.duration)}
                </span>
              )}
            </div>
          </div>

          {item.tags?.length > 0 && (
            <div className="flex gap-1.5 mt-3 flex-wrap">
              {item.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-white/[0.05] text-white/50"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
}
