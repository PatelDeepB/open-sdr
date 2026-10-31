from typing import Optional
import httpx

from opensdr.enrichment.waterfall import BaseEnrichmentProvider
from opensdr.models import EmailStatus, EnrichmentResult, Lead


class ApolloProvider(BaseEnrichmentProvider):
    """Enrichment provider integrating with Apollo.io People Match API."""

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 5.0):
        self.api_key = api_key
        self.timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "apollo_io"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        """Call Apollo People Match endpoint if API key is configured."""
        if not self.api_key:
            return EnrichmentResult(provider_name=self.name, found=False)

        if not lead.domain or not lead.first_name:
            return EnrichmentResult(provider_name=self.name, found=False)

        url = "https://api.apollo.io/v1/people/match"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        body = {
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "organization_name": lead.company_name,
            "domain": lead.domain
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=body, headers=headers)
                if res.status_code != 200:
                    return EnrichmentResult(provider_name=self.name, found=False)

                payload = res.json()
                person = payload.get("person") or {}
                email = person.get("email")
                ext_status = person.get("email_status", "")

                if email:
                    status = EmailStatus.VERIFIED if ext_status == "verified" else EmailStatus.RISKY
                    return EnrichmentResult(
                        provider_name=self.name,
                        found=True,
                        email=email,
                        status=status,
                        confidence=0.90 if status == EmailStatus.VERIFIED else 0.70,
                        extra_details={"title": person.get("title")}
                    )

                return EnrichmentResult(provider_name=self.name, found=False)
        except Exception:
            return EnrichmentResult(provider_name=self.name, found=False)
