import pytest
from fastapi.testclient import TestClient

from opensdr.api import app
from opensdr.jobs.queue import JobQueueManager, JobStatus
from opensdr.jobs.worker import run_batch_enrichment_worker
from opensdr.models import Lead

client = TestClient(app)


def test_should_manage_job_lifecycle():
    # Arrange
    manager = JobQueueManager()
    job = manager.create_job(total_items=2)

    # Act 1: mark running
    manager.mark_running(job.id)
    assert job.status == JobStatus.RUNNING

    # Act 2: update progress item 1
    manager.update_progress(job.id, success=True)
    assert job.processed_items == 1
    assert job.progress_percent == 50.0
    assert job.status == JobStatus.RUNNING

    # Act 3: update progress item 2
    manager.update_progress(job.id, success=True)
    assert job.processed_items == 2
    assert job.progress_percent == 100.0
    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None


def test_should_submit_and_poll_batch_job_via_api():
    # Arrange
    payload = {
        "leads": [
            {
                "first_name": "Peter",
                "last_name": "Parker",
                "company_name": "Daily Bugle",
                "domain": "dailybugle.mock"
            }
        ]
    }

    # Act 1: Submit batch job
    res = client.post("/api/v1/jobs/batch", json=payload)
    assert res.status_code == 202
    job_data = res.json()
    job_id = job_data["id"]
    assert job_data["total_items"] == 1

    # Act 2: Poll job status
    poll_res = client.get(f"/api/v1/jobs/{job_id}")
    assert poll_res.status_code == 200
    polled_job = poll_res.json()
    assert polled_job["id"] == job_id


@pytest.mark.asyncio
async def test_should_execute_worker_and_update_job():
    # Arrange
    manager = JobQueueManager()
    lead = Lead(
        first_name="Wade",
        last_name="Wilson",
        company_name="Weapon X",
        domain="weaponx.mock"
    )
    job = manager.create_job(total_items=1)

    # Act
    await run_batch_enrichment_worker(job.id, [lead], manager)

    # Assert
    assert job.status == JobStatus.COMPLETED
    assert job.processed_items == 1
    assert job.successful_items == 1
