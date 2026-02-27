"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { submitPodcast } from "@/lib/api";

type Status = "idle" | "loading" | "success" | "error";

export function SubmitPodcast() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setStatus("loading");
    setMessage("");

    try {
      const res = await submitPodcast(url.trim());
      setStatus("success");
      setMessage(res.message);
      setUrl("");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-2">Add a Source</h2>
        <p className="text-sm text-white/50">
          Paste any YouTube URL, podcast RSS feed, or direct audio link.
          The engine will download, transcribe, and curate the best insights for your feed.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="glass rounded-2xl p-1 flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=... or podcast RSS URL"
            className="flex-1 bg-transparent px-4 py-3 text-sm outline-none placeholder:text-white/20"
            required
          />
          <button
            type="submit"
            disabled={status === "loading" || !url.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-semibold transition-all"
          >
            {status === "loading" ? "Processing..." : "Ingest"}
          </button>
        </div>

        {message && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-xl px-4 py-3 text-sm ${
              status === "success"
                ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                : "bg-red-500/10 border border-red-500/20 text-red-400"
            }`}
          >
            {status === "success" ? "✓ " : "✗ "}
            {message}
          </motion.div>
        )}
      </form>

      <div className="mt-10 space-y-3">
        <p className="text-xs text-white/30 uppercase tracking-wider font-medium">
          What happens next
        </p>
        {[
          { icon: "⬇️", label: "Download", desc: "Audio extracted via yt-dlp" },
          { icon: "🎤", label: "Transcribe", desc: "Word-level timestamps with Whisper" },
          { icon: "🧠", label: "Curate", desc: "LLM removes fluff, keeps insights" },
          { icon: "🗄️", label: "Deduplicate", desc: "Knowledge Graph filters what you know" },
          { icon: "🎙️", label: "Narrate", desc: "AI Co-Host stitches the final feed" },
        ].map((step, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <span className="text-base w-6 shrink-0">{step.icon}</span>
            <div>
              <span className="font-medium text-white/80">{step.label}</span>
              <span className="text-white/40 ml-2">{step.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
