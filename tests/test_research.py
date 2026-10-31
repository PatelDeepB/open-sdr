import pytest
from opensdr.models import Lead
from opensdr.research.agent import HeuristicSynthesizer, ResearchAgent
from opensdr.research.crawler import clean_html_content, detect_tech_signals


def test_should_strip_scripts_and_extract_clean_text():
    # Arrange
    raw_html = """
    <html>
        <head><script>alert('malicious')</script></head>
        <body>
            <header>Site Header</header>
            <h1>Welcome to CloudScale</h1>
            <p>We provide automated cloud infrastructure for modern teams.</p>
            <footer>Footer content</footer>
        </body>
    </html>
    """

    # Act
    cleaned = clean_html_content(raw_html)

    # Assert
    assert "alert" not in cleaned
    assert "Welcome to CloudScale" in cleaned
    assert "automated cloud infrastructure" in cleaned


def test_should_detect_tech_signals_from_html():
    # Arrange
    html_with_scripts = """
    <div>
        <script src="https://js.stripe.com/v3/"></script>
        <script src="https://js.hs-scripts.com/12345.js"></script>
        <div id="root" data-reactroot=""></div>
    </div>
    """

    # Act
    signals = detect_tech_signals(html_with_scripts)

    # Assert
    assert "Stripe Payments" in signals
    assert "HubSpot CRM" in signals
    assert "React Frontend" in signals


@pytest.mark.asyncio
async def test_should_synthesize_company_research_for_lead():
    # Arrange
    lead = Lead(
        first_name="Elena",
        last_name="Rostova",
        company_name="Vanguard AI",
        domain="vanguard.ai"
    )
    mock_page_data = {
        "title": "Vanguard AI - Enterprise Autonomous Agents",
        "meta_description": "Building self-healing backend agent infrastructure for scale.",
        "body_snippet": "We solve enterprise bottlenecks and scaling pains."
    }
    synthesizer = HeuristicSynthesizer()

    # Act
    insights = await synthesizer.synthesize(lead, mock_page_data)

    # Assert
    assert "Building self-healing" in insights["summary"]
    assert "enterprise" in insights["pain_points"].lower()


@pytest.mark.asyncio
async def test_should_attach_company_info_during_agent_analysis():
    # Arrange
    class MockSynthesizer(HeuristicSynthesizer):
        async def synthesize(self, lead, page_data):
            return {
                "summary": "AI Sales Platform",
                "pain_points": "High manual SDR costs",
                "trigger": "Recent funding round"
            }

    agent = ResearchAgent(synthesizer=MockSynthesizer())
    lead = Lead(
        first_name="Marcus",
        last_name="Vance",
        company_name="Apex Global",
        domain="apexglobal.mock"
    )

    # Act
    analyzed_lead = await agent.analyze(lead)

    # Assert
    assert analyzed_lead.company_info is not None
    assert analyzed_lead.company_info.name == "Apex Global"
    assert "High manual SDR costs" in analyzed_lead.research_summary
    assert analyzed_lead.metadata.get("research_completed") is True
