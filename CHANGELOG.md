# Changelog

All notable changes to the `open-sdr` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
