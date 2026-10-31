import pytest
from fastapi.testclient import TestClient
from opensdr.api import app
from opensdr.inbound.agent import InboundSDRAgent
from opensdr.inbound.classifier import ReplyIntent, classify_inbound_reply
from opensdr.models import CampaignStatus, Lead

client = TestClient(app)


def test_should_classify_interested_reply():
    # Arrange
    reply = "Hey Alex, this sounds interesting. What does pricing look like and are you open to a call?"

    # Act
    analysis = classify_inbound_reply(reply)

    # Assert
    assert analysis.intent == ReplyIntent.INTERESTED
    assert analysis.confidence >= 0.90


def test_should_classify_unsubscribe_request():
    # Arrange
    reply = "Please unsubscribe me and remove me from your database."

    # Act
    analysis = classify_inbound_reply(reply)

    # Assert
    assert analysis.intent == ReplyIntent.UNSUBSCRIBE
    assert analysis.confidence >= 0.95


def test_should_classify_referral_and_extract_email():
    # Arrange
    reply = "I am not the right person for this. Please reach out to sarah.connor@cyberdyne.com instead."

    # Act
    analysis = classify_inbound_reply(reply)

    # Assert
    assert analysis.intent == ReplyIntent.WRONG_PERSON
    assert analysis.referral_email == "sarah.connor@cyberdyne.com"


def test_should_generate_booking_link_for_interested_lead():
    # Arrange
    lead = Lead(
        first_name="Arthur",
        last_name="Dent",
        company_name="Magrathea",
        domain="magrathea.mock",
        email="arthur@magrathea.mock"
    )
    agent = InboundSDRAgent(booking_url="https://cal.com/pateldeep/15min", sender_name="Alex")
    reply = "Sounds good, let's talk next week."

    # Act
    action = agent.process_reply(lead, reply)

    # Assert
    assert action.intent == ReplyIntent.INTERESTED
    assert "https://cal.com/pateldeep/15min" in action.draft_body
    assert action.updated_lead_status == CampaignStatus.REPLIED


def test_should_auto_create_referral_lead_on_colleague_intro():
    # Arrange
    lead = Lead(
        first_name="Bruce",
        last_name="Wayne",
        company_name="Wayne Enterprises",
        domain="wayne.mock",
        email="bruce@wayne.mock"
    )
    agent = InboundSDRAgent()
    reply = "Passed this to lucius.fox@wayne.mock who handles our infrastructure."

    # Act
    action = agent.process_reply(lead, reply)

    # Assert
    assert action.intent == ReplyIntent.WRONG_PERSON
    assert action.referral_lead is not None
    assert action.referral_lead.email == "lucius.fox@wayne.mock"
    assert action.referral_lead.metadata["referred_by"] == "bruce@wayne.mock"


def test_should_process_inbound_reply_via_api():
    # Arrange
    payload = {
        "lead": {
            "first_name": "Tony",
            "last_name": "Stark",
            "company_name": "Stark Industries",
            "domain": "stark.mock",
            "email": "tony@stark.mock"
        },
        "reply_text": "Sounds good, let's schedule a demo.",
        "booking_url": "https://cal.com/team/demo"
    }

    # Act
    response = client.post("/api/v1/inbound/reply", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "interested"
    assert "https://cal.com/team/demo" in data["draft_body"]
