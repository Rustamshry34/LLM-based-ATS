import pytest
from unittest.mock import patch, MagicMock, Mock
from database_integration import (
    save_candidate, save_job, delete_candidate, delete_job,
    Candidate, Job, session
)


def test_save_candidate_success():
    """Test saving a candidate to the database."""
    with patch('database_integration.session') as mock_session:
        mock_candidate = Mock()
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        parsed_data = {
            "name": "John Doe",
            "location": "New York",
            "experience": "5 years in software development",
            "education": "BSc Computer Science",
            "skills": "Python, JavaScript, SQL"
        }

        save_candidate(parsed_data, "unique-test-id")

        # Verify that session.add and session.commit were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_save_job_success():
    """Test saving a job to the database."""
    with patch('database_integration.session') as mock_session:
        mock_job = Mock()
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        save_job("Software Engineer", "Looking for experienced developer", "job-unique-id")

        # Verify that session.add and session.commit were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_delete_candidate_exists():
    """Test deleting a candidate that exists in the database."""
    with patch('database_integration.session') as mock_session:
        mock_candidate = Mock()
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value.first.return_value = mock_candidate
        mock_session.delete.return_value = None
        mock_session.commit.return_value = None

        result = delete_candidate("existing-id")

        assert result is True
        mock_session.delete.assert_called_once_with(mock_candidate)
        mock_session.commit.assert_called_once()


def test_delete_candidate_not_exists():
    """Test deleting a candidate that does not exist in the database."""
    with patch('database_integration.session') as mock_session:
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value.first.return_value = None

        result = delete_candidate("non-existing-id")

        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()


def test_delete_job_exists():
    """Test deleting a job that exists in the database."""
    with patch('database_integration.session') as mock_session:
        mock_job = Mock()
        mock_query = Mock()
        mock_filter_result = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value.first.return_value = mock_job
        mock_session.delete.return_value = None
        mock_session.commit.return_value = None

        result = delete_job("existing-job-id")

        assert result is True
        mock_session.delete.assert_called_once_with(mock_job)
        mock_session.commit.assert_called_once()


def test_delete_job_not_exists():
    """Test deleting a job that does not exist in the database."""
    with patch('database_integration.session') as mock_session:
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value.first.return_value = None

        result = delete_job("non-existing-job-id")

        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()


def test_candidate_model_attributes():
    """Test Candidate model attributes."""
    candidate = Candidate(
        unique_id="test-id",
        name="John Doe",
        location="New York",
        experience="5 years",
        education="BSc",
        skills="Python, SQL"
    )

    assert candidate.unique_id == "test-id"
    assert candidate.name == "John Doe"
    assert candidate.location == "New York"
    assert candidate.experience == "5 years"
    assert candidate.education == "BSc"
    assert candidate.skills == "Python, SQL"


def test_job_model_attributes():
    """Test Job model attributes."""
    job = Job(
        unique_id="job-test-id",
        title="Software Engineer",
        description="Looking for experienced developer"
    )

    assert job.unique_id == "job-test-id"
    assert job.title == "Software Engineer"
    assert job.description == "Looking for experienced developer"


def test_save_candidate_with_none_values():
    """Test saving a candidate with None values."""
    with patch('database_integration.session') as mock_session:
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        parsed_data = {
            "name": "Jane Smith",
            "location": "London",
            "experience": None,
            "education": None,
            "skills": None
        }

        save_candidate(parsed_data, "unique-test-id")

        # Should still call add and commit even with None values
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_save_job_with_special_characters():
    """Test saving a job with special characters in description."""
    with patch('database_integration.session') as mock_session:
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        save_job(
            "Software Engineer & Developer",
            "Looking for experienced developer with skills in C++, JavaScript, & Python",
            "special-chars-job-id"
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main()
