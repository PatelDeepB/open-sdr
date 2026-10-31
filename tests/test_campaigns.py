import pytest
from opensdr.campaigns.dispatcher import InboxAccount, InboxRotator, MockDispatcher
from opensdr.campaigns.orchestrator import Campaign, CampaignOrchestrator
from opensdr.models import CampaignStatus, Lead


def test_should_rotate_inboxes_evenly():
    # Arrange
    inbox_a = InboxAccount(email="a@outbound.io", display_name="Sender A", daily_limit=2)
    inbox_b = InboxAccount(email="b@outbound.io", display_name="Sender B", daily_limit=2)
    rotator = InboxRotator(inboxes=[inbox_a, inbox_b])

    # Act
    pick_1 = rotator.get_next_available_inbox()
    pick_2 = rotator.get_next_available_inbox()
    pick_3 = rotator.get_next_available_inbox()

    # Assert
    assert pick_1.email == "a@outbound.io"
    assert pick_2.email == "b@outbound.io"
    assert pick_3.email == "a@outbound.io"


def test_should_skip_inboxes_when_capacity_reached():
    # Arrange
    capped_inbox = InboxAccount(email="capped@outbound.io", display_name="Capped", daily_limit=1, sent_today=1)
    open_inbox = InboxAccount(email="open@outbound.io", display_name="Open", daily_limit=5, sent_today=0)
    rotator = InboxRotator(inboxes=[capped_inbox, open_inbox])

    # Act
    chosen = rotator.get_next_available_inbox()

    # Assert
    assert chosen.email == "open@outbound.io"


@pytest.mark.asyncio
async def test_should_dispatch_campaign_batch_and_record_metrics():
    # Arrange
    inbox = InboxAccount(email="sales@reach.io", display_name="Sales Team", daily_limit=10)
    rotator = InboxRotator(inboxes=[inbox])
    dispatcher = MockDispatcher()
    orchestrator = CampaignOrchestrator(rotator=rotator, dispatcher=dispatcher)

    lead_1 = Lead(
        first_name="David",
        last_name="Kim",
        company_name="AeroDynamics",
        domain="aerodynamics.mock",
        email="david@aerodynamics.mock",
        campaign_status=CampaignStatus.COPY_GENERATED,
        generated_copy={"initial_subject": "Hello David", "initial_body": "Are you free?"}
    )
    campaign = Campaign(id="camp_001", name="Q4 Outbound", leads=[lead_1])

    # Act
    stats = await orchestrator.dispatch_next_step(campaign)

    # Assert
    assert stats.sent_count == 1
    assert lead_1.campaign_status == CampaignStatus.SENT
    assert len(dispatcher.dispatched_messages) == 1
    assert dispatcher.dispatched_messages[0]["to"] == "david@aerodynamics.mock"

    # Act 2: Record a reply
    orchestrator.record_lead_reply(campaign, "david@aerodynamics.mock")

    # Assert 2
    assert campaign.stats.replied_count == 1
    assert campaign.stats.reply_rate == 1.0
    assert lead_1.campaign_status == CampaignStatus.REPLIED
