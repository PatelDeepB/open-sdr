import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from opensdr.api import app
from opensdr.campaigns.dispatcher import InboxAccount, SmtpDispatcher
from opensdr.db import Base, LeadRecord, save_or_update_lead
from opensdr.inbound.classifier import ReplyIntent
from opensdr.inbound.listener import ImapInboxListener
from opensdr.models import EmailStatus, Lead

test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_should_sync_inbound_messages_against_db_leads():
    # Arrange
    session = TestingSessionLocal()
    lead = Lead(
        first_name="Natasha",
        last_name="Romanoff",
        company_name="Red Room Corp",
        domain="redroom.mock",
        email="natasha@redroom.mock",
        email_status=EmailStatus.VERIFIED
    )
    save_or_update_lead(session, lead)

    listener = ImapInboxListener(booking_url="https://cal.com/sdr/15min")
    incoming_messages = [
        {
            "from_email": "natasha@redroom.mock",
            "subject": "Re: Outreach",
            "body": "Sounds good! Are you free for a call this Thursday?"
        }
    ]

    # Act
    actions = listener.sync_replies_for_session(session, incoming_messages)

    # Assert
    assert len(actions) == 1
    assert actions[0].intent == ReplyIntent.INTERESTED
    assert "https://cal.com/sdr/15min" in actions[0].draft_body

    # Verify DB lead status was updated
    updated_rec = session.query(LeadRecord).filter(LeadRecord.email == "natasha@redroom.mock").first()
    assert updated_rec.campaign_status == "replied"
    session.close()


@pytest.mark.asyncio
async def test_should_gracefully_handle_smtp_connection_failure():
    # Arrange
    dispatcher = SmtpDispatcher(host="invalid.smtp.host.local", port=587)
    inbox = InboxAccount(email="test@outbound.mock", display_name="Test", daily_limit=10)

    # Act
    dispatched = await dispatcher.send_message(
        sender_inbox=inbox,
        recipient_email="target@mock.local",
        subject="Hello",
        body="Message body"
    )

    # Assert
    assert dispatched is False


def test_should_call_inbound_sync_endpoint_via_api():
    # Arrange
    payload = {
        "booking_url": "https://cal.com/team/demo",
        "incoming_messages": []
    }

    # Act
    response = client.post("/api/v1/inbound/sync", json=payload)

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
