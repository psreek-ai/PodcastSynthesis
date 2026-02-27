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
