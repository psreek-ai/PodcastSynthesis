const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface FeedItem {
  id: string;
  title: string;
  source: string;
  audio_url: string;
  duration: number;
  tags: string[];
  knowledge_density: string;
  created_at?: string;
}

export interface FeedResponse {
  feed: FeedItem[];
}

export interface ProcessResponse {
  status: string;
  url: string;
  message: string;
}

export interface ConfigStatus {
  has_claude: boolean;
  has_spotify: boolean;
  has_elevenlabs: boolean;
  has_gemini: boolean;
  has_spotify_token: boolean;
  tts_provider: "elevenlabs" | "gemini" | "none";
}

export interface KnowledgeConcept {
  id: string;
  text: string;
  source: string;
  task_id: string;
}

export interface KnowledgeHistoryResponse {
  concepts: KnowledgeConcept[];
  total: number;
}

export interface SpotifyShow {
  id: string;
  name: string;
  publisher: string;
  description: string;
  image: string | null;
  episodes_total: number;
}

/** Fetch the curated knowledge feed. */
export async function getFeed(): Promise<FeedItem[]> {
  const res = await fetch(`${API_BASE}/api/feed`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch feed: ${res.statusText}`);
  const data: FeedResponse = await res.json();
  return data.feed;
}

/** Submit a podcast URL for processing. */
export async function submitPodcast(url: string): Promise<ProcessResponse> {
  const res = await fetch(`${API_BASE}/api/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error(`Failed to submit: ${res.statusText}`);
  return res.json();
}

/** Get API key configuration status. */
export async function getConfigStatus(): Promise<ConfigStatus> {
  const res = await fetch(`${API_BASE}/api/config`);
  if (!res.ok) throw new Error(`Config check failed: ${res.statusText}`);
  return res.json();
}

/** Ask the AI Co-Host a question about the current context. */
export async function askCoHost(
  query: string,
  context: string
): Promise<{ answer_text: string }> {
  const res = await fetch(`${API_BASE}/api/chat/interrupt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_query_text: query,
      current_podcast_context: context,
    }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.statusText}`);
  return res.json();
}

/** Fetch concepts stored in the user's Knowledge Graph. */
export async function getKnowledgeHistory(): Promise<KnowledgeHistoryResponse> {
  const res = await fetch(`${API_BASE}/api/knowledge/history`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch knowledge history: ${res.statusText}`);
  return res.json();
}

/** Delete a concept from the Knowledge Graph by ID. */
export async function deleteKnowledgeConcept(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/knowledge/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Failed to delete concept: ${res.statusText}`);
}

/** Fetch the user's saved Spotify shows (requires Spotify OAuth). */
export async function getSpotifyShows(): Promise<{ shows: SpotifyShow[]; total: number }> {
  const res = await fetch(`${API_BASE}/api/spotify/shows`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch Spotify shows: ${res.statusText}`);
  return res.json();
}
