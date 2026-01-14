import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np
from api import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ATS system!"}


@patch('api.parse_resume_with_llm')
@patch('api.save_candidate')
def test_upload_resume_success(mock_save_candidate, mock_parse_resume, client):
    """Test successful resume upload."""
    # Mock the return values
    mock_parse_resume.return_value = ({"unique_id": "test-id"}, [0.1, 0.2, 0.3])
    mock_save_candidate.return_value = None

    # Create a mock PDF file
    pdf_content = b"%PDF-1.4 test pdf content"

    response = client.post(
        "/upload-resume/",
        data={
            "name": "John Doe",
            "location": "New York"
        },
        files={"file": ("test.pdf", pdf_content, "application/pdf")}
    )

    assert response.status_code == 200
    assert "Resume uploaded successfully" in response.json()["message"]
    mock_parse_resume.assert_called_once()


def test_upload_resume_missing_name(client):
    """Test resume upload with missing name."""
    pdf_content = b"%PDF-1.4 test pdf content"

    response = client.post(
        "/upload-resume/",
        data={
            "name": "",  # Empty name
            "location": "New York"
        },
        files={"file": ("test.pdf", pdf_content, "application/pdf")}
    )

    assert response.status_code == 400
    assert "Name cannot be empty" in response.json()["detail"]


def test_upload_resume_invalid_file_type(client):
    """Test resume upload with invalid file type."""
    txt_content = b"This is a text file"

    response = client.post(
        "/upload-resume/",
        data={
            "name": "John Doe",
            "location": "New York"
        },
        files={"file": ("test.txt", txt_content, "text/plain")}
    )

    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]


@patch('api.generate_embedding')
@patch('api.add_to_job_chroma')
@patch('api.save_job')
def test_post_job_success(mock_save_job, mock_add_to_chroma, mock_generate_embedding, client):
    """Test successful job posting."""
    mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_add_to_chroma.return_value = "job-test-id"
    mock_save_job.return_value = None

    response = client.post(
        "/post-job/",
        data={
            "job_title": "Software Engineer",
            "job_description": "We are looking for a software engineer..."
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Job posted successfully"


def test_post_job_empty_description(client):
    """Test job posting with empty description."""
    response = client.post(
        "/post-job/",
        data={
            "job_title": "Software Engineer",
            "job_description": ""  # Empty description
        }
    )

    assert response.status_code == 400
    assert "Job description cannot be empty" in response.json()["detail"]


@patch('api.get_all_jobs_from_chroma')
def test_match_candidates_success(mock_get_jobs, client):
    """Test successful candidate matching."""
    mock_get_jobs.return_value = (
        ["job1"],
        [[0.1, 0.2, 0.3]],
        [{"title": "Software Engineer", "description": "Looking for engineer"}]
    )

    with patch('api.calculate_ats_score') as mock_calculate:
        mock_calculate.return_value = [
            {
                "candidate_id": "candidate1",
                "score": 0.95,
                "metadata": {"name": "John Doe"}
            }
        ]

        response = client.get("/match-candidates/")

        assert response.status_code == 200
        assert "results" in response.json()
        assert len(response.json()["results"]) == 1


@patch('api.delete_resume_from_chroma')
@patch('api.delete_candidate')
def test_delete_resume_success(mock_delete_candidate, mock_delete_from_chroma, client):
    """Test successful resume deletion."""
    mock_delete_candidate.return_value = True

    response = client.delete("/delete-resume/", params={"unique_id": "test-id"})

    assert response.status_code == 200
    assert response.json()["message"] == "Resume deleted successfully"
    mock_delete_from_chroma.assert_called_once_with("test-id")


@patch('api.delete_job_from_chroma')
@patch('api.delete_job')
def test_delete_job_success(mock_delete_job, mock_delete_from_chroma, client):
    """Test successful job deletion."""
    mock_delete_job.return_value = True

    response = client.delete("/delete-job/", params={"unique_id": "test-id"})

    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted successfully"
    mock_delete_from_chroma.assert_called_once_with("test-id")


def test_validation_error_handling(client):
    """Test validation error handling."""
    # Missing required fields
    response = client.post("/post-job/", data={})

    assert response.status_code == 422
    assert response.json()["message"] == "Validation error"
