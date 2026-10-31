# OpenSDR

> Production-ready, 100% open-source alternative to Clay and autonomous AI SDRs (like 11x).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Tests: Passing](https://img.shields.io/badge/Tests-31%20Passing-success.svg)](tests/)

OpenSDR replicates the core feature set of high-ticket outbound sales platforms (like Clay and 11x) without per-credit fees or vendor lock-in.

---

## Architecture Overview

```
Raw Lead (CSV / Web UI / API)
        │
        ▼
[Waterfall Enrichment Engine]  ──► 1. Free Web Scraper
        │                          2. Email Permutation Generator
        │                          3. DNS / MX Server Verifier
        │                          4. Modular Providers (Hunter, Apollo)
        ▼
[Autonomous Web Research]      ──► Crawls Target Domain (/about, meta tags)
        │                          Detects Tech Stack (HubSpot, Stripe, AWS, React)
        ▼
[AI Copywriter & Auditor]      ──► Dynamic Icebreaker from Researched Signals
        │                          3-Touch Sequence (Initial, Bump, Breakup)
        │                          Deliverability & Spam Auditor
        ▼
[Campaign Orchestrator]        ──► Multi-Inbox Rotation & Daily Quota Guard
        │                          Mock & Webhook Dispatchers
        │                          Live Reply & Bounce Analytics
        ▼
[Autonomous Inbound SDR]       ──► Classifies Replies (Interested, Referral, Opt-out)
                                   Embeds Cal.com / Calendly Links Automatically
                                   Auto-Creates New Leads from Referrals
```

---

## Key Features

1. **Interactive Spreadsheet Grid:** Airtable/Clay style web spreadsheet at `http://localhost:8000` with live cell progress, single-click row execution, and instant prospect management.
2. **Waterfall Lead Enrichment Engine:** Cascades through free web scrapers, email permutation generators, live DNS/MX validators, and optional Hunter/Apollo APIs.
3. **Credit & Cost Tracking:** Automatically tracks API calls and counts credits saved by free upstream providers.
4. **Autonomous Web Research Agent:** Analyzes target company domains, career pages, and meta descriptions to synthesize buying triggers and tech stacks.
5. **AI Outreach Copywriter:** Generates hyper-tailored 3-touch cadences (`quick_question`, `pas`, `followup_bump`, `breakup`) with bespoke icebreakers.
6. **Deliverability & Spam Auditor:** Scans copy against commercial spam filters, penalizes bloated subject lines, and optimizes for mobile readability.
7. **Autonomous Inbound SDR (11x Feature):** Parses incoming prospect email replies, classifies intent, auto-schedules meetings via Cal.com/Calendly, and extracts colleague referrals.
8. **Campaign Management:** Rotates multiple sender accounts with daily quota caps to protect domain health.

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

### 1. Launch Interactive Spreadsheet Grid UI

Start the local server:

```bash
uvicorn opensdr.api:app --reload --port 8000
```

Open your browser to:
👉 **`http://localhost:8000`**

From the UI, you can:
* Add custom prospect rows.
* Run real-time waterfall enrichment on live domains.
* Use the **Inbound SDR Simulator** to test automated intent classification and calendar link generation.

---

### 2. Command-Line Interface (CLI)

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

### 3. REST API Endpoints

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

* `GET /` : Interactive spreadsheet dashboard UI.
* `GET /health` : System and dependency health status.
* `POST /api/v1/enrich` : Execute waterfall enrichment cascade.
* `POST /api/v1/research` : Crawl domain and extract firmographics.
* `POST /api/v1/copywrite` : Generate 3-step sequence and deliverability audit.
* `POST /api/v1/pipeline` : End-to-end SDR run (Enrich -> Research -> Copywrite).
* `POST /api/v1/inbound/reply` : Autonomous SDR reply classification and calendar booking.

---

## Running Tests

Execute the complete test suite:

```bash
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
