# Contributing to AI Podcast Engine 2.0

Thank you for your interest in contributing! This document covers how to get started, the v3 roadmap, and our development workflow.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Decisions](#architecture-decisions)
- [Roadmap & Open Issues](#roadmap--open-issues)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Testing](#testing)

---

## Getting Started

1. **Star the repository** — it helps more developers find this project
2. Check [open issues](../../issues) for things labeled `good first issue` or `help wanted`
3. If you want to build something new, open an issue first to discuss

---

## Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/podcast-engine-2.0.git
cd podcast-engine-2.0

# Install everything
make install

# Copy env template
cp .env.example .env

# Run the stack
make dev
```

For local-only development (no API keys required):
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3

# Set in .env
USE_LOCAL_LLM=true
```

---

## Architecture Decisions

Understanding why things are built the way they are:

| Decision | Rationale |
|---|---|
| **FastAPI** over Django/Flask | Async-first, auto-generates OpenAPI docs, Pydantic validation |
| **LiteLLM router** | Swaps Claude ↔ Ollama with one flag; future-proof for new LLMs |
| **ChromaDB** over Pinecone | Local-first; no API costs; persistent file-based storage |
| **SQLite** for feed | Zero config; single file; trivially replaceable with Postgres |
| **yt-dlp** over Spotify SDK | Works on YouTube, RSS, direct URLs; Spotify API is restrictive |
| **Whisper local** | Privacy-first; no per-minute transcription cost; works offline |
| **FFmpeg subprocess** | More control than ffmpeg-python wrappers; battle-tested |

---

## Roadmap & Open Issues

### v2.1 (Bug Fixes & Polish)
- [ ] Fix audio slicer to actually extract timestamps from LLM output
- [ ] Persist task status to DB so users can track pipeline progress
- [ ] Rate limiting on `/api/process` to prevent abuse
- [ ] Input validation for submitted URLs
- [ ] Handle corrupt/empty audio files gracefully

### v2.5 (Frontend)
- [ ] Build the Next.js feed player UI
- [ ] 3D Knowledge Graph visualization (React Force Graph 3D)
- [ ] Settings page for API key configuration
- [ ] Mobile-responsive audio player with waveform

### v3.0 (Major Features)
- [ ] **Real-time streaming** — WebSocket push for live feed updates
- [ ] **Multi-speaker diarization** — filter by specific podcast guests
- [ ] **Spotify integration** — auto-ingest from saved shows
- [ ] **Newsletter export** — weekly HTML email digest
- [ ] **Video podcast support** — extract visual frames + timestamps
- [ ] **Multi-user** — separate knowledge graphs per user with auth
- [ ] **Mobile app** — React Native feed player

### Stretch Goals
- [ ] Plugin system for custom LLM prompts
- [ ] Podcast recommendation engine (collaborative filtering on knowledge graphs)
- [ ] Browser extension to clip any web audio

---

## Submitting Changes

### Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes** with clear, focused commits:
   ```bash
   git commit -m "feat: add speaker diarization to transcription pipeline"
   git commit -m "fix: handle empty transcript segments in LLM analysis"
   ```

3. **Run CI checks locally** before pushing:
   ```bash
   make ci
   ```

4. **Open a Pull Request** with:
   - A clear title describing the change
   - Context on *why* the change is needed
   - Screenshots/recordings for UI changes
   - Link to the related issue

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`

---

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Format
make format

# Check (what CI runs)
make lint
```

Key conventions:
- Python 3.10+ type hints on all public functions
- Docstrings for all classes and public methods
- Avoid magic numbers — use named constants or env vars
- Prefer `logging` over `print` statements

---

## Testing

```bash
# Run all tests
make test

# With coverage
make test-cov
```

When adding features, please add corresponding tests:
- **API changes** → `backend/tests/test_api.py`
- **Database changes** → `backend/tests/test_database.py`
- **Media/FFmpeg changes** → `backend/tests/test_media.py`
- **LLM/AI changes** → mock the LLM call (see `conftest.py`)

Use the existing mock fixtures in `conftest.py` to avoid making real API calls in tests.

---

## Questions?

Open an issue labeled `question` or start a [Discussion](../../discussions).

We're building this in the open. All skill levels welcome.
