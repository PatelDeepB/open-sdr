import enum
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class JobStatus(str, enum.Enum):
    """Execution status of a background asynchronous job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Job status, execution counters, and progress report."""
    id: str
    status: JobStatus = JobStatus.PENDING
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    progress_percent: float = 0.0
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class JobQueueManager:
    """Manages creation, tracking, and state transitions for background jobs."""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}

    def create_job(self, total_items: int) -> Job:
        """Initialize a new job with a unique UUID."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = Job(id=job_id, total_items=total_items)
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Fetch job state by ID."""
        return self._jobs.get(job_id)

    def mark_running(self, job_id: str) -> Optional[Job]:
        """Set job state to RUNNING."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.RUNNING
        return job

    def update_progress(self, job_id: str, success: bool, error: Optional[str] = None) -> Optional[Job]:
        """Increment progress counter and recalculate completion percentage."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        job.processed_items += 1
        if success:
            job.successful_items += 1
        else:
            job.failed_items += 1
            if error:
                job.errors.append(error)

        if job.total_items > 0:
            job.progress_percent = round((job.processed_items / job.total_items) * 100.0, 1)

        if job.processed_items >= job.total_items:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)

        return job
