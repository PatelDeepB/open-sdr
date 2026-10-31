import pytest
from fastapi.testclient import TestClient
from opensdr.api import app

client = TestClient(app)


def test_should_return_healthy_status_on_health_check():
    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["dependencies"]["enricher"] == "operational"


def test_should_fail_with_400_when_missing_required_enrichment_fields():
    # Arrange
    invalid_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "TestCo",
        "domain": ""
    }

    # Act
    response = client.post("/api/v1/enrich", json=invalid_payload)

    # Assert
    assert response.status_code == 400
    assert "Domain and first_name are required" in response.json()["detail"]


def test_should_execute_full_pipeline_via_api():
    # Arrange
    payload = {
        "first_name": "Alice",
        "last_name": "Wonder",
        "company_name": "Wonderland Tech",
        "domain": "wonderland.mock",
        "template_name": "quick_question"
    }

    # Act
    response = client.post("/api/v1/pipeline", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["email"] is not None
    assert "initial_subject" in data["generated_copy"]
    assert "initial_body" in data["generated_copy"]
