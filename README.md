# OpenSDR

> Production-ready, 100% open-source alternative to Clay and autonomous AI SDRs (like 11x).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](docker-compose.yml)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org)
[![Tests: Passing](https://img.shields.io/badge/Tests-47%20Passing-success.svg)](tests/)
[![Zero API Keys Required](https://img.shields.io/badge/API%20Keys-Zero%20Required-success.svg)]()

OpenSDR replicates the core feature set of high-ticket outbound sales platforms without per-credit fees or vendor lock-in.

---

## Do I Need Any API Keys to Use OpenSDR?

**No. OpenSDR is 100% operational out of the box with zero API keys required.**

* **Email Discovery & Verification:** Uses free web scrapers, corporate permutation heuristics, and direct live DNS MX server validation for $0.
* **Firmographic Research:** Crawls company domains, parses meta descriptions, and extracts tech stacks without third-party subscriptions.
* **AI Analysis & Copywriting:** Built-in deterministic NLP engine handles icebreakers, pain point detection, and 3-touch sequence generation completely free.
* **Optional Paid Keys:** If you choose to add external keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `HUNTER_API_KEY`, or `APOLLO_API_KEY`), OpenSDR automatically routes through them. When OpenAI is configured, it defaults to the high-efficiency **GPT-6 Luna** model.

---

## Comparison Matrix: OpenSDR vs Commercial Tools

| Feature | OpenSDR | Clay.com | 11x.ai (Alice) | Apollo.io |
| :--- | :---: | :---: | :---: | :---: |
| **Pricing** | **$0 / month** | $149 to $800+/mo | $3,000+/mo | $99/mo |
| **Source Code** | **100% Open-Source (MIT)** | Closed SaaS | Closed SaaS | Closed SaaS |
| **Self-Hosted & Private** | **Yes (Local / Docker)** | No (Cloud Only) | No (Cloud Only) | No (Cloud Only) |
| **Interactive Spreadsheet Grid** | **Yes** | Yes | No | Table View |
| **Waterfall Lead Enrichment** | **Yes** | Yes | No | Basic Match |
| **Autonomous Web Research Agent** | **Yes** | Yes (Claygent) | Yes | Basic Signals |
| **AI Outreach Copywriter** | **Yes** | Yes | Yes | Yes |
| **Autonomous Inbound SDR** | **Yes** | No | Yes | No |
| **Calendar Booking Integration** | **Yes (Cal.com / Calendly)** | No | Yes | Basic |
| **Persistent Database Storage** | **Yes (SQLite / Postgres)** | Cloud DB | Cloud DB | Cloud DB |
| **Async Background Job Queue** | **Yes** | Yes | Yes | Yes |
| **One-Click Docker Deploy** | **Yes** | No | No | No |

---

## Architecture Overview

```
Prospects (CSV Import / Web UI / REST API)
        │
        ▼
[SQLAlchemy Persistent Storage]  ──► SQLite / PostgreSQL Engine
        │
        ▼
[Background Job Worker Queue]   ──► Asyncio & Concurrency Runner (No Timeouts)
        │
        ▼
[Waterfall Enrichment Engine]   ──► 1. Free Web Scraper
        │                           2. Email Permutation Generator
        │                           3. DNS / MX Server Verifier
        │                           4. Modular Providers (Hunter, Apollo)
        ▼
[Universal Multi-LLM Engine]    ──► Auto-Detects Gemini, OpenAI (GPT-6 Luna), Ollama
        │                           Crawl & Extract Buying Triggers + Tech Stacks
        ▼
[AI Copywriter & Auditor]       ──► Dynamic Icebreaker from Researched Signals
        │                           3-Touch Sequence (Initial, Bump, Breakup)
        │                           Deliverability & Spam Auditor
        ▼
[Campaign Orchestrator]         ──► Multi-Inbox Rotation & Daily Quota Guard
        │                           TLS SMTP & Webhook Dispatchers
        │                           Live Reply & Bounce Analytics
        ▼
[Autonomous Inbound SDR]        ──► IMAP Mailbox Listener
                                    Classifies Replies (Interested, Referral, Opt-out)
                                    Embeds Cal.com / Calendly Links Automatically
                                    Auto-Creates New Leads from Referrals
```

---

## Quickstart

### Option A: One-Click Docker Deployment

```bash
git clone https://github.com/PatelDeepB/open-sdr.git
cd open-sdr
docker compose up -d
```

Open your browser to:
👉 **`http://localhost:8000`**

---

### Option B: Local Python Setup

```bash
git clone https://github.com/PatelDeepB/open-sdr.git
cd open-sdr
pip install -e .
uvicorn opensdr.api:app --reload --port 8000
```

---

### Command-Line Interface (CLI)

#### Run Full Pipeline for a Single Lead

```bash
python -m opensdr.cli pipeline \
  --first-name "Satya" \
  --last-name "Nadella" \
  --company "Microsoft" \
  --domain "microsoft.com"
```

#### Batch Process Leads from CSV

```bash
python -m opensdr.cli batch --file data/sample_leads.csv --output results.json
```

---

## Environment Variables (All Optional)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///data/opensdr.db` |
| `GEMINI_API_KEY` | Google Gemini API key for advanced research | Empty (uses heuristic) |
| `OPENAI_API_KEY` | OpenAI API key | Empty (uses heuristic) |
| `OPENAI_MODEL` | OpenAI Model ID (defaults to GPT-6 Luna) | `gpt-6-luna` |
| `OLLAMA_HOST` | Local Ollama instance URL | `http://localhost:11434` |
| `HUNTER_API_KEY` | Optional Hunter.io enrichment key | Empty (skips gracefully) |
| `APOLLO_API_KEY` | Optional Apollo.io enrichment key | Empty (skips gracefully) |

---

## Running Tests

Execute the complete test suite:

```bash
pytest
```

---

## Star History

If OpenSDR has saved you money on Clay or 11x subscriptions, consider starring the repo:

[![Star History Chart](https://api.star-history.com/svg?repos=PatelDeepB/open-sdr&type=Date)](https://star-history.com/#PatelDeepB/open-sdr&Date)

---

## Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) and our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
