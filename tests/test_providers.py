import pytest
from opensdr.enrichment.providers.apollo import ApolloProvider
from opensdr.enrichment.providers.hunter import HunterProvider
from opensdr.enrichment.waterfall import (
    BaseEnrichmentProvider,
    WaterfallEnricher,
    create_standard_waterfall,
)
from opensdr.models import EmailStatus, EnrichmentResult, Lead


@pytest.mark.asyncio
async def test_should_gracefully_skip_hunter_without_api_key():
    # Arrange
    provider = HunterProvider(api_key=None)
    lead = Lead(first_name="Jane", last_name="Doe", company_name="Acme", domain="acme.mock")

    # Act
    result = await provider.enrich_lead(lead)

    # Assert
    assert result.found is False
    assert result.provider_name == "hunter_io"


@pytest.mark.asyncio
async def test_should_gracefully_skip_apollo_without_api_key():
    # Arrange
    provider = ApolloProvider(api_key=None)
    lead = Lead(first_name="Jane", last_name="Doe", company_name="Acme", domain="acme.mock")

    # Act
    result = await provider.enrich_lead(lead)

    # Assert
    assert result.found is False
    assert result.provider_name == "apollo_io"


@pytest.mark.asyncio
async def test_should_track_credits_saved_when_early_provider_succeeds():
    # Arrange
    class MockFreeProvider(BaseEnrichmentProvider):
        @property
        def name(self) -> str:
            return "free_hero"

        async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
            return EnrichmentResult(
                provider_name=self.name,
                found=True,
                email="jane@acme.mock",
                status=EmailStatus.VERIFIED,
                confidence=1.0
            )

    class MockPaidProvider1(BaseEnrichmentProvider):
        @property
        def name(self) -> str:
            return "paid_provider_1"

        async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
            return EnrichmentResult(provider_name=self.name, found=False)

    class MockPaidProvider2(BaseEnrichmentProvider):
        @property
        def name(self) -> str:
            return "paid_provider_2"

        async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
            return EnrichmentResult(provider_name=self.name, found=False)

    enricher = WaterfallEnricher(
        providers=[MockFreeProvider(), MockPaidProvider1(), MockPaidProvider2()]
    )
    lead = Lead(first_name="Jane", last_name="Doe", company_name="Acme", domain="acme.mock")

    # Act
    enriched_lead = await enricher.run(lead)

    # Assert
    assert enriched_lead.email == "jane@acme.mock"
    assert enricher.credits_saved == 2
    assert enricher.call_counts["free_hero"] == 1
    assert enricher.call_counts["paid_provider_1"] == 0
    assert enricher.call_counts["paid_provider_2"] == 0


def test_should_wire_all_providers_in_standard_waterfall():
    # Act
    enricher = create_standard_waterfall(
        hunter_api_key="mock_hunter_key",
        apollo_api_key="mock_apollo_key"
    )

    # Assert
    provider_names = [p.name for p in enricher.providers]
    assert "free_website_scraper" in provider_names
    assert "permutation_verifier" in provider_names
    assert "hunter_io" in provider_names
    assert "apollo_io" in provider_names
    assert len(provider_names) == 4
