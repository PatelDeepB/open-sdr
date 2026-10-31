# Changelog

All notable changes to the `open-sdr` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
