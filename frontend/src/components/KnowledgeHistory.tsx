"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  KnowledgeConcept,
  deleteKnowledgeConcept,
  getKnowledgeHistory,
} from "@/lib/api";

/**
 * KnowledgeHistory — shows concepts stored in the user's ChromaDB Knowledge Graph.
 *
 * Inspired by PodcastKnowledgeDistiller's Knowledge History tab:
 * - Lists every concept the engine has learned from your podcasts
 * - Shows the source URL so you know where the insight came from
 * - Lets you delete individual concepts to "forget" them
 * - Total count helps you gauge how rich your personal knowledge graph is
 */
export function KnowledgeHistory() {
  const [concepts, setConcepts] = useState<KnowledgeConcept[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    getKnowledgeHistory()
      .then((data) => {
        setConcepts(data.concepts);
        setTotal(data.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteKnowledgeConcept(id);
      setConcepts((prev) => prev.filter((c) => c.id !== id));
      setTotal((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Failed to delete concept:", err);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass rounded-2xl p-4 animate-pulse">
            <div className="h-3 bg-white/5 rounded w-full mb-2" />
            <div className="h-3 bg-white/5 rounded w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (!concepts.length) {
    return (
      <div className="text-center py-20 text-white/40">
        <div className="text-4xl mb-4">🧠</div>
        <p className="text-lg font-medium text-white/60">Knowledge Graph is empty</p>
        <p className="text-sm mt-1">
          Process some podcasts to start building your personal knowledge base.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Knowledge Graph</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-white/40">{total} concepts learned</span>
          {concepts.length < total && (
            <span className="text-xs text-white/30">(showing {concepts.length})</span>
          )}
        </div>
      </div>

      <AnimatePresence>
        {concepts.map((concept, idx) => (
          <motion.div
            key={concept.id}
            layout
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20, height: 0, marginBottom: 0 }}
            transition={{ delay: idx * 0.03, layout: { duration: 0.2 } }}
            className="glass rounded-2xl p-4 group"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-2 h-2 rounded-full bg-indigo-400/60 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/80 leading-relaxed">{concept.text}</p>
                {concept.source && (
                  <p
                    className="text-xs text-white/30 mt-1.5 truncate"
                    title={concept.source}
                  >
                    {concept.source}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDelete(concept.id)}
                disabled={deletingId === concept.id}
                className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 w-6 h-6 flex items-center justify-center rounded-md hover:bg-red-500/20 text-red-400/60 hover:text-red-400 text-xs"
                title="Remove from knowledge graph"
              >
                {deletingId === concept.id ? "…" : "✕"}
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
