import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from opensdr.api import app
from opensdr.db import (
    Base,
    LeadRecord,
    list_leads,
    save_or_update_lead,
)
from opensdr.models import EmailStatus, Lead

# In-memory database for isolated unit tests
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_should_persist_and_retrieve_lead():
    # Arrange
    session = TestingSessionLocal()
    lead = Lead(
        first_name="Bruce",
        last_name="Wayne",
        company_name="Wayne Enterprises",
        domain="wayne.mock",
        email="bruce@wayne.mock",
        email_status=EmailStatus.VERIFIED
    )

    # Act
    record = save_or_update_lead(session, lead)
    retrieved = list_leads(session)

    # Assert
    assert record.id is not None
    assert len(retrieved) >= 1
    assert retrieved[0].first_name == "Bruce"
    assert retrieved[0].email == "bruce@wayne.mock"
    session.close()


def test_should_update_existing_record_without_duplication():
    # Arrange
    session = TestingSessionLocal()
    lead = Lead(
        first_name="Clark",
        last_name="Kent",
        company_name="Daily Planet",
        domain="dailyplanet.mock"
    )
    record = save_or_update_lead(session, lead)
    initial_id = record.id

    # Act
    lead.email = "clark@dailyplanet.mock"
    lead.email_status = EmailStatus.VERIFIED
    updated_record = save_or_update_lead(session, lead)

    # Assert
    assert updated_record.id == initial_id
    assert updated_record.email == "clark@dailyplanet.mock"
    session.close()


def test_should_handle_lead_crud_via_api():
    # Act 1: Create a lead via API
    lead_payload = {
        "first_name": "Diana",
        "last_name": "Prince",
        "company_name": "Themyscira Labs",
        "domain": "themyscira.mock"
    }
    create_res = client.post("/api/v1/leads", json=lead_payload)
    assert create_res.status_code == 200
    created_id = create_res.json()["id"]

    # Act 2: Fetch list of leads
    list_res = client.get("/api/v1/leads")
    assert list_res.status_code == 200
    leads = list_res.json()
    assert any(l["first_name"] == "Diana" for l in leads)

    # Act 3: Delete lead
    del_res = client.delete(f"/api/v1/leads/{created_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True
