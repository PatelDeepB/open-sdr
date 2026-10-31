import abc
import re
from typing import Dict, List, Optional
import httpx

from opensdr.enrichment.verifier import (
    generate_email_permutations,
    verify_email_candidate,
)
from opensdr.models import EmailStatus, EnrichmentResult, Lead


class BaseEnrichmentProvider(abc.ABC):
    """Abstract interface for all enrichment providers in the waterfall."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider."""
        pass

    @abc.abstractmethod
    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        """Attempt to discover and verify an email for the given lead."""
        pass


class WebsiteScraperProvider(BaseEnrichmentProvider):
    """Free provider that searches the company website for public email addresses."""

    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "free_website_scraper"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        if not lead.domain:
            return EnrichmentResult(provider_name=self.name, found=False)

        target_url = f"https://{lead.domain}"
        found_emails = await self._scrape_page_emails(target_url)

        first = lead.first_name.lower()
        last = lead.last_name.lower()

        for candidate in found_emails:
            lower_candidate = candidate.lower()
            if first in lower_candidate or (last and last in lower_candidate):
                verification = verify_email_candidate(candidate, check_dns=False)
                return EnrichmentResult(
                    provider_name=self.name,
                    found=True,
                    email=candidate,
                    status=verification.status,
                    confidence=0.85,
                    extra_details={"source_url": target_url}
                )

        return EnrichmentResult(provider_name=self.name, found=False)

    async def _scrape_page_emails(self, url: str) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return []
                matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
                return list(set(matches))
        except Exception:
            return []


class PermutationHeuristicProvider(BaseEnrichmentProvider):
    """Generates standard corporate email permutations and verifies active MX records."""

    def __init__(self, check_dns: bool = True):
        self.check_dns = check_dns

    @property
    def name(self) -> str:
        return "permutation_verifier"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        candidates = generate_email_permutations(
            first_name=lead.first_name,
            last_name=lead.last_name,
            domain=lead.domain
        )
        if not candidates:
            return EnrichmentResult(provider_name=self.name, found=False)

        primary_candidate = candidates[0]
        verification = verify_email_candidate(primary_candidate, check_dns=self.check_dns)

        if verification.status == EmailStatus.VERIFIED:
            return EnrichmentResult(
                provider_name=self.name,
                found=True,
                email=primary_candidate,
                status=EmailStatus.VERIFIED,
                confidence=verification.confidence,
                extra_details={"generated_permutations": len(candidates)}
            )

        return EnrichmentResult(provider_name=self.name, found=False)


class WaterfallEnricher:
    """Cascading orchestrator that executes enrichment providers sequentially until verified."""

    def __init__(self, providers: Optional[List[BaseEnrichmentProvider]] = None):
        self.providers: List[BaseEnrichmentProvider] = providers or [
            WebsiteScraperProvider(),
            PermutationHeuristicProvider()
        ]
        self.call_counts: Dict[str, int] = {p.name: 0 for p in self.providers}
        self.credits_saved: int = 0

    async def run(self, lead: Lead) -> Lead:
        """Execute the waterfall sequence across configured providers for a lead."""
        for idx, provider in enumerate(self.providers):
            self.call_counts[provider.name] = self.call_counts.get(provider.name, 0) + 1
            result = await provider.enrich_lead(lead)
            if result.found and result.email:
                lead.email = result.email
                lead.email_status = result.status
                lead.confidence_score = result.confidence
                lead.metadata["enriched_by"] = result.provider_name
                lead.metadata["enrichment_details"] = result.extra_details
                
                # Count remaining skipped providers as credits/calls saved
                skipped = len(self.providers) - (idx + 1)
                self.credits_saved += skipped
                lead.metadata["waterfall_steps_skipped"] = skipped
                return lead

        lead.email_status = EmailStatus.INVALID
        lead.confidence_score = 0.0
        return lead


def create_standard_waterfall(
    hunter_api_key: Optional[str] = None,
    apollo_api_key: Optional[str] = None
) -> WaterfallEnricher:
    """Construct a full enterprise-tier waterfall cascading from free to paid APIs."""
    from opensdr.enrichment.providers.apollo import ApolloProvider
    from opensdr.enrichment.providers.hunter import HunterProvider

    providers: List[BaseEnrichmentProvider] = [
        WebsiteScraperProvider(),
        PermutationHeuristicProvider()
    ]
    if hunter_api_key:
        providers.append(HunterProvider(api_key=hunter_api_key))
    if apollo_api_key:
        providers.append(ApolloProvider(api_key=apollo_api_key))

    return WaterfallEnricher(providers=providers)
