import pytest
from opensdr.enrichment.verifier import (
    generate_email_permutations,
    is_disposable_domain,
    is_valid_syntax,
    verify_email_candidate,
)
from opensdr.enrichment.waterfall import (
    BaseEnrichmentProvider,
    WaterfallEnricher,
)
from opensdr.models import EmailStatus, EnrichmentResult, Lead


def test_should_generate_valid_email_permutations():
    # Arrange
    first = "Sarah"
    last = "Connor"
    domain = "cyberdyne.com"

    # Act
    permutations = generate_email_permutations(first, last, domain)

    # Assert
    assert "sarah.connor@cyberdyne.com" in permutations
    assert "sarahconnor@cyberdyne.com" in permutations
    assert "sconnor@cyberdyne.com" in permutations
    assert "sarah@cyberdyne.com" in permutations


def test_should_reject_invalid_email_syntax():
    # Arrange
    invalid_email = "plainaddress-without-at"

    # Act
    is_valid = is_valid_syntax(invalid_email)

    # Assert
    assert is_valid is False


def test_should_detect_disposable_domain():
    # Arrange
    disposable_domain = "mailinator.com"

    # Act
    is_disposable = is_disposable_domain(disposable_domain)

    # Assert
    assert is_disposable is True


def test_should_flag_disposable_candidate_as_invalid():
    # Arrange
    candidate = "test@tempmail.com"

    # Act
    result = verify_email_candidate(candidate, check_dns=False)

    # Assert
    assert result.status == EmailStatus.INVALID
    assert result.is_disposable is True


class MockAlwaysFailsProvider(BaseEnrichmentProvider):
    @property
    def name(self) -> str:
        return "mock_failing_provider"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        return EnrichmentResult(provider_name=self.name, found=False)


class MockSuccessfulProvider(BaseEnrichmentProvider):
    @property
    def name(self) -> str:
        return "mock_success_provider"

    async def enrich_lead(self, lead: Lead) -> EnrichmentResult:
        return EnrichmentResult(
            provider_name=self.name,
            found=True,
            email=f"{lead.first_name.lower()}@{lead.domain}",
            status=EmailStatus.VERIFIED,
            confidence=0.9
        )


@pytest.mark.asyncio
async def test_should_cascade_waterfall_until_provider_succeeds():
    # Arrange
    failing_provider = MockAlwaysFailsProvider()
    success_provider = MockSuccessfulProvider()
    enricher = WaterfallEnricher(providers=[failing_provider, success_provider])

    target_lead = Lead(
        first_name="Alex",
        last_name="Murphy",
        company_name="OmniCorp",
        domain="omnicorp.com"
    )

    # Act
    enriched = await enricher.run(target_lead)

    # Assert
    assert enriched.email == "alex@omnicorp.com"
    assert enriched.email_status == EmailStatus.VERIFIED
    assert enriched.metadata["enriched_by"] == "mock_success_provider"
