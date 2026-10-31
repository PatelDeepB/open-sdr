import pytest
from opensdr.campaigns.dispatcher import InboxAccount, InboxRotator, MockDispatcher
from opensdr.campaigns.orchestrator import Campaign, CampaignOrchestrator
from opensdr.cli import execute_lead_pipeline
from opensdr.models import CampaignStatus, Lead


@pytest.mark.asyncio
async def test_should_execute_end_to_end_sdr_workflow():
    # Arrange
    raw_lead = Lead(
        first_name="Victor",
        last_name="Stone",
        company_name="Cyborg Systems",
        domain="cyborg.mock"
    )

    # Act 1: Execute autonomous pipeline (Enrichment + Research + Copywriting)
    processed_lead = await execute_lead_pipeline(raw_lead, template_name="pas")

    # Assert 1: Lead is enriched, researched, and copy generated
    assert processed_lead.email == "victor.stone@cyborg.mock"
    assert processed_lead.company_info is not None
    assert processed_lead.campaign_status == CampaignStatus.COPY_GENERATED
    assert "initial_subject" in processed_lead.generated_copy
    assert "followup_subject" in processed_lead.generated_copy
    assert "breakup_subject" in processed_lead.generated_copy

    # Act 2: Dispatch through Campaign Orchestrator
    inbox = InboxAccount(email="founder@growth.io", display_name="Founder", daily_limit=50)
    rotator = InboxRotator(inboxes=[inbox])
    dispatcher = MockDispatcher()
    orchestrator = CampaignOrchestrator(rotator=rotator, dispatcher=dispatcher)

    campaign = Campaign(id="e2e_camp", name="E2E Pipeline Test", leads=[processed_lead])
    stats = await orchestrator.dispatch_next_step(campaign)

    # Assert 2: Lead transitioned to SENT, metrics updated
    assert stats.sent_count == 1
    assert processed_lead.campaign_status == CampaignStatus.SENT
    assert len(dispatcher.dispatched_messages) == 1
    assert dispatcher.dispatched_messages[0]["to"] == "victor.stone@cyborg.mock"
    assert "Cyborg Systems" in dispatcher.dispatched_messages[0]["subject"]
