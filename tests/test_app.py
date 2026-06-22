from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.app import app, cleanup_job, scheduler

client = TestClient(app)

# -- Test the root endpoint --


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FlowChunk API!"}


# -- Test the cleanup job --


@patch("app.app.run_user_cleanup")
@patch("app.app.SessionLocal")
def test_cleanup_calls_run_user_cleanup(
    mock_session_local: MagicMock, mock_run_user_cleanup: MagicMock
):
    db = MagicMock()
    mock_session_local.return_value = db

    cleanup_job()

    mock_session_local.assert_called_once()
    mock_run_user_cleanup.assert_called_once_with(db)
    db.close.assert_called_once()


@patch("app.app.run_user_cleanup")
@patch("app.app.SessionLocal")
def test_cleanup_job_closes_db_even_on_exception(
    mock_session_local: MagicMock, mock_run_user_cleanup: MagicMock
):
    db = MagicMock()
    mock_session_local.return_value = db
    mock_run_user_cleanup.side_effect = Exception("Cleanup failed")

    with pytest.raises(Exception, match="Cleanup failed"):
        cleanup_job()
    mock_session_local.assert_called_once()
    mock_run_user_cleanup.assert_called_once_with(db)
    db.close.assert_called_once()


# -- Test the scheduler setup --


def test_scheduler_started():
    assert scheduler.running is True


def test_scheduler_has_cleanup_job_registered():
    jobs = scheduler.get_jobs()

    assert len(jobs) == 1

    job = jobs[0]

    assert job.func == cleanup_job

    assert str(job.trigger) == "cron[hour='0', minute='0']"


def test_scheduler_job_configuration():
    job = scheduler.get_jobs()[0]

    fields = {field.name: str(field) for field in job.trigger.fields}

    assert fields["hour"] == "0"
    assert fields["minute"] == "0"
