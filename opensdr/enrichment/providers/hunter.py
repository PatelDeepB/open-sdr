from typing import Optional
import httpx

from opensdr.enrichment.waterfall import BaseEnrichmentProvider
from opensdr.models import EmailStatus, EnrichmentResult, Lead


class HunterProvider(BaseEnrichmentProvider):
    """Enrichment provider integrating with Hunter.io Email Finder API."""

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 5.0):
        self.api_key = api_key
        self.timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "hunter_io"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        """Call Hunter Email Finder endpoint if API key is present."""
        if not self.api_key:
            return EnrichmentResult(provider_name=self.name, found=False)

        if not lead.domain or not lead.first_name:
            return EnrichmentResult(provider_name=self.name, found=False)

        url = "https://api.hunter.io/v2/email-finder"
        params = {
            "domain": lead.domain,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "api_key": self.api_key
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, params=params)
                if res.status_code != 200:
                    return EnrichmentResult(provider_name=self.name, found=False)

                payload = res.json()
                data = payload.get("data", {})
                email = data.get("email")
                score = (data.get("score") or 0) / 100.0

                if email:
                    return EnrichmentResult(
                        provider_name=self.name,
                        found=True,
                        email=email,
                        status=EmailStatus.VERIFIED if score >= 0.70 else EmailStatus.RISKY,
                        confidence=score,
                        extra_details={"hunter_score": data.get("score")}
                    )

                return EnrichmentResult(provider_name=self.name, found=False)
        except Exception:
            return EnrichmentResult(provider_name=self.name, found=False)
