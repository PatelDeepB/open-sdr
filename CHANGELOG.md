# Changelog

All notable changes to the `open-sdr` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 16: OpenAI Model Upgrade to GPT-6 Luna - 2026-10-31
- Upgraded OpenAI default model ID from legacy 4o-mini to `gpt-6-luna` in `opensdr.ai`.
- Added dynamic model selection via `OPENAI_MODEL` environment variable.
- Updated `docker-compose.yml` to pass through `OPENAI_MODEL=${OPENAI_MODEL:-gpt-6-luna}`.
- Added 2 unit tests in `tests/test_ai.py` verifying default and custom model configurations.
- Updated documentation and environment variable references in `README.md`.

### Phase 15: GitHub SEO, Community Health & Open-Source Perfection - 2026-10-31
- Added GitHub issue templates for bug reports and feature requests.
- Added GitHub pull request template.
- Added open-source community health standards: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.
- Enhanced `README.md` with cost comparison matrix (OpenSDR vs Clay vs 11x vs Apollo), CI badges, Star History chart, and zero-API-key guarantee.
- Added 10 SEO topics on remote GitHub repository: `ai-agent`, `clay-alternative`, `sdr`, `lead-generation`, `cold-email`, `sales-automation`, `waterfall-enrichment`, `fastapi`, `llm`, `open-source`.

### Phase 14: Production Containerization & Docker Compose - 2026-10-31
- Added production-grade `Dockerfile` based on `python:3.11-slim` with automated curl healthcheck.
- Added `docker-compose.yml` supporting persistent volume mounts for the SQLite database.
- Added `.dockerignore` for lean container builds.
- Added environment variable routing for `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `OLLAMA_HOST`.
- Updated `README.md` with one-command container deployment guide (`docker compose up -d`).

### Phase 13: Universal Multi-LLM Engine (Gemini, OpenAI, Ollama) - 2026-10-31
- Added `UniversalLLMClient` in `opensdr.ai` with multi-model routing (Google Gemini, OpenAI GPT-4o-mini, local Ollama).
- Implemented automatic environment credential detection (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `OLLAMA_HOST`).
- Implemented zero-cost deterministic NLP fallback so the platform operates fully even when offline or without paid keys.
- Integrated `LLMSynthesizer` into `ResearchAgent` for deep firmographic analysis.
- Added 5 unit tests in `tests/test_ai.py`.

### Phase 12: Full Web UI Persistence, CSV Import/Export & Live Job Polling - 2026-10-31
- Connected the web spreadsheet UI dynamically to `GET /api/v1/leads` database records on load.
- Implemented in-browser CSV import parsing and bulk creation via `POST /api/v1/leads`.
- Implemented in-browser CSV export with all enriched attributes and AI outreach copy.
- Integrated background task progress banner polling `GET /api/v1/jobs/{id}` with live progress percentage.
- Added prospect creation modal, deletion controls, and status filtering tabs (All, Verified, Replied).
- Updated `README.md` with enterprise architecture and user workflows.

### Phase 11: Real-Time IMAP Mailbox Listener & Production SMTP Dispatcher - 2026-10-31
- Added `ImapInboxListener` in `opensdr.inbound.listener` for monitoring unread emails and thread responses.
- Implemented automated matching of incoming emails against database prospects.
- Built automated trigger: when an incoming email matches an active lead, the SDR classifies intent, embeds Cal.com/Calendly links, and updates lead status to `REPLIED`.
- Added `SmtpDispatcher` in `opensdr.campaigns.dispatcher` supporting TLS, authenticated SMTP servers, and MIME multipart messages.
- Exposed `POST /api/v1/inbound/sync` endpoint for scheduled or webhook-based inbox synchronization.
- Added 3 unit tests in `tests/test_listener.py`.

### Phase 10: Asynchronous Background Job Engine & Task Queue - 2026-10-31
- Added `Job` and `JobStatus` models with tracking for progress percentage, processed items, and errors.
- Implemented `JobQueueManager` for job creation, status updates, and completion recording.
- Implemented `run_batch_enrichment_worker` in `opensdr.jobs.worker` to process large lead lists asynchronously in the background.
- Added API endpoints in `opensdr.api`: `POST /api/v1/jobs/batch` (202 Accepted) and `GET /api/v1/jobs/{job_id}`.
- Added 3 unit tests in `tests/test_jobs.py`.

### Phase 9: Persistent Database & ORM Storage - 2026-10-31
- Added `LeadRecord` SQLAlchemy ORM model and SQLite/PostgreSQL storage in `opensdr.db`.
- Added bidirectional serialization between database records and Pydantic `Lead` models.
- Implemented `save_or_update_lead`, `list_leads`, and session generator `get_db`.
- Added CRUD endpoints in `opensdr.api`: `GET /api/v1/leads`, `POST /api/v1/leads`, and `DELETE /api/v1/leads/{id}`.
- Configured automated persistence in `POST /api/v1/pipeline` so all enriched leads persist across restarts.
- Added 3 database and API tests in `tests/test_db.py`.

### Phase 8: Interactive Spreadsheet Web UI and Execution Grid - 2026-10-31
- Created interactive Clay-style web spreadsheet dashboard in `opensdr/static/index.html`.
- Implemented real-time single-row and batch waterfall execution from the web browser.
- Built interactive Inbound SDR Simulator drawer to test automated reply classification and booking link generation.
- Mounted dashboard endpoints at `/` and `/dashboard` in `opensdr.api`.
- Added dashboard route test in `tests/test_api.py`.
- Updated `README.md` with UI screenshots guide and complete architecture flow.

### Phase 7: Autonomous Inbound Reply Classifier and Calendar Booking Agent - 2026-10-31
- Added `classify_inbound_reply` in `opensdr.inbound.classifier` to classify prospect intent (`INTERESTED`, `OBJECTION`, `WRONG_PERSON`, `OUT_OF_OFFICE`, `UNSUBSCRIBE`).
- Added entity extraction for referral colleague emails within incoming messages.
- Implemented `InboundSDRAgent` that auto-generates context-aware replies with dynamic calendar booking links (Cal.com / Calendly).
- Added auto-creation of referral `Lead` records when a prospect refers a colleague.
- Added suppression list flag for unsubscribe requests.
- Exposed `POST /api/v1/inbound/reply` API endpoint.
- Added 6 unit tests in `tests/test_inbound.py`.

### Phase 6: Multi-Provider API Integrations and Credit Tracking - 2026-10-31
- Added `HunterProvider` integrating with Hunter.io Email Finder API.
- Added `ApolloProvider` integrating with Apollo.io People Match API.
- Added credit and API call tracking on `WaterfallEnricher` (`call_counts`, `credits_saved`).
- Added `create_standard_waterfall` factory for seamless multi-provider chaining from free to paid APIs.
- Added 4 unit tests in `tests/test_providers.py`.

### Phase 5: REST API, CLI Interface, and End-to-End Pipeline - 2026-10-31
- Implemented FastAPI REST API server in `opensdr.api` with explicit `/api/v1/` versioning and `/health` monitoring.
- Built command-line interface in `opensdr.cli` with single prospect pipeline execution and CSV batch processing.
- Added sample dataset in `data/sample_leads.csv`.
- Added API tests in `tests/test_api.py` and end-to-end integration test in `tests/test_pipeline.py`.
- Updated `README.md` with comprehensive architectural diagram, CLI manual, and quickstart guide.

### Phase 4: Campaign Management, Outbound Sequencing, and Dispatch Engine - 2026-10-31
- Added `InboxAccount` and `InboxRotator` for multi-inbox rotation and daily sending quota protection.
- Built `BaseDispatcher`, `MockDispatcher` (for safe dry-runs/simulations), and `WebhookDispatcher` (for CRM/automation triggers).
- Implemented `CampaignOrchestrator` for lead status tracking (`QUEUED`, `SENT`, `REPLIED`, `BOUNCED`).
- Built automated real-time campaign statistics calculations (reply rates, bounce rates, sent counts).
- Added 3 unit tests in `tests/test_campaigns.py`.

### Phase 3: AI Copywriter, Personalization Engine, and Deliverability Checker - 2026-10-31
- Added `audit_email_deliverability` engine in `opensdr.copywriting.deliverability` with spam phrase penalty algorithms.
- Implemented high-converting outbound templates (`quick_question`, `pas`, `followup_bump`, and `breakup`).
- Built `CopywriterAgent` to generate personalized 3-step outreach cadences using researched firmographic data.
- Structured automated icebreaker creation driven by detected tech stack and company signals.
- Added 4 unit tests in `tests/test_copywriting.py`.

### Phase 2: Autonomous Web Research Agent (Claygent Equivalent) - 2026-10-31
- Implemented HTML cleaner and metadata extractor in `opensdr.research.crawler`.
- Added automated tech stack detection (HubSpot, Salesforce, Stripe, Shopify, React, AWS, etc.).
- Implemented `ResearchAgent` and `HeuristicSynthesizer` for zero-cost automated research.
- Structured company profiles with value proposition, pain point analysis, and buying triggers.
- Added comprehensive unit tests in `tests/test_research.py`.

### Phase 1: Core Models and Waterfall Enrichment Engine - 2026-10-31
- Added domain models: `Lead`, `Company`, `EmailStatus`, `CampaignStatus`, `EmailVerificationResult`, and `EnrichmentResult`.
- Implemented email permutation generator supporting standard corporate formats.
- Implemented multi-tier email verifier (RFC syntax checking, disposable domain detection, and DNS MX record validation).
- Implemented `WaterfallEnricher` with cascading provider support (`WebsiteScraperProvider`, `PermutationHeuristicProvider`).
- Added unit tests covering permutation generation, disposable detection, syntax parsing, and waterfall cascading.

### Initial Setup - 2026-10-31
- Created base project repository structure.
- Added MIT License and `.gitignore`.
- Configured Python build system in `pyproject.toml`.
- Initialized public GitHub repository at `PatelDeepB/open-sdr`.
