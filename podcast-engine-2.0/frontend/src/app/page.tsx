"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FeedPlayer } from "@/components/FeedPlayer";
import { SubmitPodcast } from "@/components/SubmitPodcast";
import { StatusBar } from "@/components/StatusBar";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<"feed" | "submit">("feed");

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-white/[0.06] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-lg">
            🎙️
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight">AI Podcast Engine</h1>
            <p className="text-xs text-white/40">Infinite knowledge feed</p>
          </div>
        </div>

        <nav className="flex gap-1 p-1 rounded-lg glass">
          {(["feed", "submit"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                activeTab === tab
                  ? "bg-white/10 text-white"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              {tab === "feed" ? "Feed" : "Add Source"}
            </button>
          ))}
        </nav>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-8">
        <AnimatePresence mode="wait">
          {activeTab === "feed" ? (
            <motion.div
              key="feed"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <FeedPlayer />
            </motion.div>
          ) : (
            <motion.div
              key="submit"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <SubmitPodcast />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Status bar */}
      <StatusBar />
    </div>
  );
}
