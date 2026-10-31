# OpenSDR

> Production-ready, 100% open-source alternative to Clay and autonomous AI SDRs (like 11x).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org)
[![Tests: Passing](https://img.shields.io/badge/Tests-40%20Passing-success.svg)](tests/)

OpenSDR replicates the core feature set of high-ticket outbound sales platforms (like Clay and 11x) without per-credit fees or vendor lock-in.

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
[Autonomous Web Research]       ──► Crawls Target Domain (/about, meta tags)
        │                           Detects Tech Stack (HubSpot, Stripe, AWS, React)
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

## Enterprise Feature Set

1. **Persistent Database Engine:** Built on SQLAlchemy with SQLite (default) and PostgreSQL compatibility. Every lead, campaign status, and AI sequence is permanently saved.
2. **Asynchronous Background Task Queue:** Run batches of 1,000+ leads without HTTP request timeouts. Live progress bars report real-time percentage and item counters.
3. **Interactive Clay-Style Spreadsheet Grid:** Web dashboard at `http://localhost:8000` with live row updates, CSV import/export, and single-click SDR runs.
4. **Waterfall Lead Enrichment:** Cascades through free web scrapers, email permutation generators, live DNS/MX validators, and optional Hunter/Apollo APIs.
5. **Credit & Cost Tracking:** Automatically tracks API calls and counts credits saved by free upstream providers.
6. **Autonomous Web Research Agent:** Analyzes target company domains, career pages, and meta descriptions to synthesize buying triggers and tech stacks.
7. **AI Outreach Copywriter:** Generates hyper-tailored 3-touch cadences (`quick_question`, `pas`, `followup_bump`, `breakup`) with bespoke icebreakers.
8. **Deliverability & Spam Auditor:** Scans copy against commercial spam filters, penalizes bloated subject lines, and optimizes for mobile readability.
9. **Autonomous Inbound SDR (11x Feature):** Parses incoming prospect email replies, classifies intent, auto-schedules meetings via Cal.com/Calendly, and extracts colleague referrals.
10. **Real-Time IMAP Mailbox Listener & SMTP Dispatcher:** Automatically monitors unread inbox replies and sends authenticated TLS emails.

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
* Add custom prospect rows into the persistent database.
* Upload CSV files directly with automatic schema mapping.
* Export enriched leads to CSV with verified emails and copy.
* Run real-time background batch jobs with live progress bars.
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
* `GET /health` : System, database, and dependency health status.
* `GET /api/v1/leads` : List all saved prospects from database.
* `POST /api/v1/leads` : Save a new lead to database.
* `DELETE /api/v1/leads/{id}` : Remove a lead from database.
* `POST /api/v1/jobs/batch` : Submit batch enrichment job to background queue (202 Accepted).
* `GET /api/v1/jobs/{job_id}` : Poll execution progress and counters for a job.
* `POST /api/v1/enrich` : Execute waterfall enrichment cascade.
* `POST /api/v1/research` : Crawl domain and extract firmographics.
* `POST /api/v1/copywrite` : Generate 3-step sequence and deliverability audit.
* `POST /api/v1/pipeline` : End-to-end SDR run (Enrich -> Research -> Copywrite -> Persist).
* `POST /api/v1/inbound/reply` : Autonomous SDR reply classification and calendar booking.
* `POST /api/v1/inbound/sync` : IMAP inbox synchronization and autonomous trigger.

---

## Running Tests

Execute the complete test suite:

```bash
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
