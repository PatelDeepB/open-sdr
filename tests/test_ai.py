import pytest
from opensdr.ai import UniversalLLMClient
from opensdr.models import Lead
from opensdr.research.agent import LLMSynthesizer


def test_should_detect_heuristic_mode_by_default():
    # Arrange
    client = UniversalLLMClient(gemini_api_key=None, openai_api_key=None)

    # Act
    provider = client.get_active_provider()

    # Assert
    assert provider == "heuristic"


def test_should_detect_gemini_provider_when_key_present():
    # Arrange
    client = UniversalLLMClient(gemini_api_key="mock_gemini_key")

    # Act
    provider = client.get_active_provider()

    # Assert
    assert provider == "gemini"


def test_should_detect_openai_provider_when_key_present():
    # Arrange
    client = UniversalLLMClient(openai_api_key="mock_openai_key")

    # Act
    provider = client.get_active_provider()

    # Assert
    assert provider == "openai"


@pytest.mark.asyncio
async def test_should_return_fallback_response_without_keys():
    # Arrange
    client = UniversalLLMClient()

    # Act
    response = await client.generate("Analyze company operational bottlenecks.")

    # Assert
    assert "bottlenecks" in response.lower() or "streamlining" in response.lower()


@pytest.mark.asyncio
async def test_should_synthesize_lead_insights_with_llm_synthesizer():
    # Arrange
    synthesizer = LLMSynthesizer()
    lead = Lead(
        first_name="Tony",
        last_name="Stark",
        company_name="Stark Tech",
        domain="starktech.mock"
    )
    page_data = {
        "title": "Stark Tech - Defense & AI Systems",
        "meta_description": "Global leaders in clean energy and intelligent automation.",
        "body_snippet": "Pioneering ARC reactors and advanced software."
    }

    # Act
    insights = await synthesizer.synthesize(lead, page_data)

    # Assert
    assert "Global leaders" in insights["summary"]
    assert len(insights["pain_points"]) > 10
