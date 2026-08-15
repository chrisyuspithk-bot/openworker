# OpenWorker

**A self-hosted AI coworker — deployed as a web app.**

OpenWorker is an open-source AI coworker that delivers **finished work**, not chat: a polished document, a Slack reply with the numbers, an updated calendar, a triaged inbox. It runs as a **web app you host yourself**, is provider-agnostic (bring any API key, or run fully local with Ollama), and keeps your data on the host that serves it.

> **Beta** — fully usable and actively polished. [Issues](https://github.com/chrisyuspithk-bot/openworker/issues) welcome.

## What it does

- **Produce real deliverables** — documents, spreadsheets, reports, and web pages land as files you can download from the browser.
- **Work across your tools** — GitHub, Slack, Jira, Notion, Linear, HubSpot, Gmail, Google Calendar, plus your terminal and local files, and anything reachable over [MCP](https://modelcontextprotocol.io/).
- **Ask before acting** — writes, sends, and shell commands are approval-gated before they run.
- **Run on a schedule** — automations for recurring work, with full transcripts.

## Bring your own model

Pick a provider, paste a key, switch anytime. Supported out of the box:

**OpenAI · Anthropic · Google Gemini · DeepSeek · Z.ai (GLM) · Kimi (Moonshot) · Qwen (Alibaba) · MiniMax · Mistral · xAI (Grok) · Meta (Muse Spark) · Together AI · Fireworks AI · OpenRouter** — plus **any OpenAI-compatible endpoint** (Groq, vLLM, LM Studio, self-hosted proxies) and fully local models via **Ollama**. AWS **Bedrock** and Google **Vertex** are supported too (Bedrock needs the optional `boto3` dependency).

## Architecture (web)

```text
┌────────────────────────────────────────────────────────────┐
│  browser  —  one origin                                     │
│    │                                                        │
│    ├── /            →  React UI (built static dist)         │
│    └── /v1/* + WS   →  FastAPI agent server (Python)        │
│                          ├── engine · tools · connectors    │
│                          └── model providers (your keys)    │
└────────────────────────────────────────────────────────────┘
```

The UI discovers its API and WebSocket endpoints from `window.location.origin` at runtime, so the same build serves from any host or behind any reverse proxy — no rebuild when the domain changes.

## Run it (web)

Prerequisites: Python 3.10+ and Node 20+.

```bash
git clone https://github.com/chrisyuspithk-bot/openworker
cd openworker

# 1. Backend
pip install -e .

# 2. Web UI -> surfaces/gui/dist
cd surfaces/gui
npm install
npm run build
cd ../..

# 3. Serve the UI and API on one origin
openworker-web --cwd ~/some/project --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`. `openworker-web` mounts the built UI next to the FastAPI app: `/` serves the app and `/v1/*` serves the agent API.

To expose it publicly, bind `--host 0.0.0.0` and put a TLS-terminating reverse proxy (nginx, Caddy, …) in front. The app runs account-less out of the box — no sign-in step.

### Access control (optional)

The web server is open by default. To require a shared token:

```bash
export COWORKER_API_TOKEN="<long-random-string>"    # server

# build the UI with the matching token baked in
cd surfaces/gui && VITE_COWORKER_API_TOKEN="$COWORKER_API_TOKEN" npm run build
```

The server checks the `X-OpenWorker-Token` header and the WebSocket subprotocol; the built UI sends the same value.

### Data & workspaces

Conversations, connector tokens, and model keys live in the standard coworker state dir (`$COWORKER_STATE_DIR`, else `~/.config/coworker` on macOS/Linux, `%APPDATA%\coworker` on Windows). `--cwd` is an optional seed workspace. Everything stays on the host.

## Privacy

OpenWorker is local-first by design, and self-hosting keeps that promise: the agent loop, conversations, connector tokens, and model keys all live on your host. The only traffic that leaves is to the model and integrations *you* configure. Use it without signing in — connectors work with manually-created credentials/API keys.

## Run from source (desktop, optional)

The web build is the same React UI used by the optional desktop shell. For the native app instead of a browser:

```bash
cd surfaces/gui
npm run tauri dev   # launches the window and supervises the server itself
```

Upstream desktop installers: [macOS (Apple Silicon)](https://download.openworker.com/mac) · [Windows 10/11 (x64)](https://download.openworker.com/windows).

## Tests

```bash
pip install -e ".[dev]"     # pytest + httpx
pytest                      # backend suite

cd surfaces/gui
npm test                    # GUI unit tests
npm run e2e                 # hermetic end-to-end
```

## Repository layout

| Directory | What's in it |
|---|---|
| `coworker/` | Python backend — agent engine, model providers, connectors, MCP client, memory, automations, and the `openworker-web` web host |
| `surfaces/gui/` | React + TypeScript web UI (also wraps the optional Tauri desktop shell) |
| `stt/` | Speech-to-text sidecar (Rust) for voice input |
| `packaging/` | Desktop installer builds and dev bootstrap |
| `docs/` | Design specs and decision logs |
| `tests/` | Backend test suite |

## Built on aisuite

OpenWorker's engine is built on [**aisuite**](https://github.com/andrewyng/aisuite), a lightweight Python library providing a unified chat-completions API across LLM providers plus an agents layer with tools, toolkits, and MCP support. If you want to build your own agent harness rather than use ours, start there; this repo is a working reference for what aisuite can carry.

OpenWorker was originally developed inside the aisuite repository before moving to its own home; thanks to the aisuite contributors whose work it builds on.

## Contributing

Contributions and bug reports are welcome — open an [issue](https://github.com/chrisyuspithk-bot/openworker/issues) or a pull request. For any PR, please attach screenshots of what was broken and how it is fixed. Note that we develop against an internal list and may not approve PRs that add features already under development or that deviate from our vision.

## License

MIT — see [LICENSE](LICENSE).
