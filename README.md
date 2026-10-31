# OpenSDR

> Production-ready, 100% open-source alternative to Clay and autonomous AI SDRs.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Tests: Passing](https://img.shields.io/badge/Tests-20%20Passing-success.svg)](tests/)

OpenSDR replicates the core feature set of high-ticket outbound sales platforms (like Clay and 11x) without per-credit fees or vendor lock-in.

---

## Architecture Overview

```
Raw Lead (CSV / API)
        │
        ▼
[Waterfall Enrichment Engine]  ──► 1. Free Web Scraper
        │                          2. Email Permutation Generator
        │                          3. DNS / MX Server Verifier
        ▼
[Autonomous Web Research]      ──► Crawls Target Domain (/about, meta tags)
        │                          Detects Tech Stack (HubSpot, Stripe, AWS, React)
        ▼
[AI Copywriter & Auditor]      ──► Dynamic Icebreaker from Signals
        │                          3-Touch Sequence (Initial, Bump, Breakup)
        │                          Deliverability & Spam Auditor
        ▼
[Campaign Orchestrator]        ──► Multi-Inbox Rotation & Daily Quota Guard
                                   Mock & Webhook Dispatchers
                                   Live Reply & Bounce Analytics
```

---

## Key Features

1. **Waterfall Lead Enrichment Engine:** Cascades through free web scrapers, company registries, email permutation generators, and live DNS/MX validators to discover and verify decision-maker contacts without wasting paid credits.
2. **Autonomous Web Research Agent:** Analyzes prospective company domains, career pages, and press mentions to extract value propositions, pain points, and buying triggers.
3. **AI Personalization Copywriter:** Automatically drafts hyper-tailored cold outreach emails (Pain-Agitate-Solution, Value-First, Quick Question) with custom icebreakers based on tech stack and market signals.
4. **Deliverability & Spam Safety Auditor:** Scans subject lines and copy for commercial spam trigger phrases, length penalties, and mobile open readability.
5. **Campaign Sequencing and Inbox Rotation:** Rotates sender inboxes with strict daily limits to protect domain reputation and tracks campaign performance (sent, replied, bounced).
6. **REST API & CLI Interface:** Full FastAPI REST API (`/api/v1/`) and standalone CLI tool (`open-sdr`) for batch CSV processing.

---

## Quickstart

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/PatelDeepB/open-sdr.git
cd open-sdr
pip install -e .
```

---

### Command-Line Interface (CLI)

#### 1. Process a Single Prospect

```bash
python -m opensdr.cli pipeline \
  --first-name "Satya" \
  --last-name "Nadella" \
  --company "Microsoft" \
  --domain "microsoft.com"
```

#### 2. Batch Process Leads from CSV

```bash
python -m opensdr.cli batch --file data/sample_leads.csv --output results.json
```

---

### REST API Server

Start the FastAPI server:

```bash
uvicorn opensdr.api:app --reload --port 8000
```

Open interactive Swagger docs at `http://localhost:8000/docs`.

#### Endpoints:

* `GET /health` : Health check and dependency status.
* `POST /api/v1/enrich` : Run waterfall enrichment on a lead.
* `POST /api/v1/research` : Crawl company domain and extract firmographics.
* `POST /api/v1/copywrite` : Generate 3-step sequence and deliverability audit.
* `POST /api/v1/pipeline` : End-to-end SDR run (Enrich -> Research -> Copywrite).

---

## Running Tests

Execute the complete test suite:

```bash
pytest
```

---

## Development Roadmap & Merged Phases

- **Phase 1:** Core Data Models & Waterfall Enrichment Engine (PR #1)
- **Phase 2:** Autonomous Web Research Agent (PR #2)
- **Phase 3:** AI Personalization Copywriter & Deliverability Checker (PR #3)
- **Phase 4:** Campaign Sequencing & Outbound Dispatcher (PR #4)
- **Phase 5:** REST API, CLI Interface, and End-to-End Pipeline (PR #5)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
