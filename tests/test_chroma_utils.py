import pytest
from unittest.mock import patch, MagicMock
import uuid
from chroma_utils import (
    add_to_resume_chroma, add_to_job_chroma,
    search_resume_chroma, get_all_jobs_from_chroma,
    delete_resume_from_chroma, delete_job_from_chroma
)


def test_add_to_resume_chroma():
    """Test adding resume to Chroma collection."""
    with patch('chroma_utils.resume_collection') as mock_collection:
        mock_collection.add.return_value = None
        embedding = [0.1, 0.2, 0.3]
        metadata = {"name": "John Doe", "location": "New York"}

        result = add_to_resume_chroma(embedding, metadata)

        # Check that the result is a valid UUID
        assert isinstance(result, str)
        uuid.UUID(result)  # This will raise an exception if not a valid UUID

        # Check that add was called with the right parameters
        mock_collection.add.assert_called_once()
        args, kwargs = mock_collection.add.call_args
        assert len(args) == 0  # All arguments should be keyword arguments
        assert "ids" in kwargs
        assert "embeddings" in kwargs
        assert "metadatas" in kwargs
        assert kwargs["embeddings"] == [embedding]
        assert kwargs["metadatas"] == [metadata]


def test_add_to_job_chroma():
    """Test adding job to Chroma collection."""
    with patch('chroma_utils.job_collection') as mock_collection:
        mock_collection.add.return_value = None
        embedding = [0.4, 0.5, 0.6]
        metadata = {"title": "Software Engineer", "description": "Looking for dev"}

        result = add_to_job_chroma(embedding, metadata)

        # Check that the result is a valid UUID
        assert isinstance(result, str)
        uuid.UUID(result)  # This will raise an exception if not a valid UUID

        # Check that add was called with the right parameters
        mock_collection.add.assert_called_once()
        args, kwargs = mock_collection.add.call_args
        assert len(args) == 0  # All arguments should be keyword arguments
        assert "ids" in kwargs
        assert "embeddings" in kwargs
        assert "metadatas" in kwargs
        assert kwargs["embeddings"] == [embedding]
        assert kwargs["metadatas"] == [metadata]


def test_search_resume_chroma():
    """Test searching resumes in Chroma collection."""
    with patch('chroma_utils.resume_collection') as mock_collection:
        mock_results = {
            'ids': [['candidate1', 'candidate2']],
            'embeddings': [[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]],
            'metadatas': [[{'name': 'John'}, {'name': 'Jane'}]]
        }
        mock_collection.query.return_value = mock_results

        query_embedding = [0.15, 0.25, 0.35]
        result = search_resume_chroma(query_embedding, k=5)

        # Check that query was called with the right parameters
        mock_collection.query.assert_called_once()
        args, kwargs = mock_collection.query.call_args
        assert kwargs["query_embeddings"] == [query_embedding]
        assert kwargs["n_results"] == 5
        assert "include" in kwargs
        assert "embeddings" in kwargs["include"]
        assert "metadatas" in kwargs["include"]

        # Check that the result matches expected format
        assert result == mock_results


def test_search_resume_chroma_default_k():
    """Test searching resumes with default k value."""
    with patch('chroma_utils.resume_collection') as mock_collection:
        mock_results = {
            'ids': [['candidate1']],
            'embeddings': [[[0.1, 0.2, 0.3]]],
            'metadatas': [[{'name': 'John'}]]
        }
        mock_collection.query.return_value = mock_results

        query_embedding = [0.15, 0.25, 0.35]
        result = search_resume_chroma(query_embedding)  # Default k=10

        # Check that query was called with default k value
        mock_collection.query.assert_called_once()
        args, kwargs = mock_collection.query.call_args
        assert kwargs["n_results"] == 10


def test_get_all_jobs_from_chroma():
    """Test getting all jobs from Chroma collection."""
    with patch('chroma_utils.job_collection') as mock_collection:
        mock_results = {
            'ids': ['job1', 'job2'],
            'embeddings': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            'metadatas': [{'title': 'Engineer', 'description': 'Dev role'}, {'title': 'Designer', 'description': 'Design role'}]
        }
        mock_collection.get.return_value = mock_results

        ids, embeddings, metadatas = get_all_jobs_from_chroma()

        # Check that get was called with the right parameters
        mock_collection.get.assert_called_once()
        args, kwargs = mock_collection.get.call_args
        assert "include" in kwargs
        assert "embeddings" in kwargs["include"]
        assert "metadatas" in kwargs["include"]

        # Check that the results are correctly extracted
        assert ids == ['job1', 'job2']
        assert embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert metadatas == [{'title': 'Engineer', 'description': 'Dev role'}, {'title': 'Designer', 'description': 'Design role'}]


def test_delete_resume_from_chroma():
    """Test deleting resume from Chroma collection."""
    with patch('chroma_utils.resume_collection') as mock_collection:
        mock_collection.delete.return_value = None

        delete_resume_from_chroma("test-resume-id")

        # Check that delete was called with the right parameters
        mock_collection.delete.assert_called_once()
        args, kwargs = mock_collection.delete.call_args
        assert "ids" in kwargs
        assert kwargs["ids"] == ["test-resume-id"]


def test_delete_job_from_chroma():
    """Test deleting job from Chroma collection."""
    with patch('chroma_utils.job_collection') as mock_collection:
        mock_collection.delete.return_value = None

        delete_job_from_chroma("test-job-id")

        # Check that delete was called with the right parameters
        mock_collection.delete.assert_called_once()
        args, kwargs = mock_collection.delete.call_args
        assert "ids" in kwargs
        assert kwargs["ids"] == ["test-job-id"]


def test_add_to_resume_chroma_multiple_calls_unique_ids():
    """Test that multiple calls to add_to_resume_chroma generate unique IDs."""
    with patch('chroma_utils.resume_collection') as mock_collection:
        mock_collection.add.return_value = None

        id1 = add_to_resume_chroma([0.1, 0.2], {"name": "John"})
        id2 = add_to_resume_chroma([0.3, 0.4], {"name": "Jane"})

        # IDs should be different
        assert id1 != id2
        # Both should be valid UUIDs
        uuid.UUID(id1)
        uuid.UUID(id2)


def test_add_to_job_chroma_multiple_calls_unique_ids():
    """Test that multiple calls to add_to_job_chroma generate unique IDs."""
    with patch('chroma_utils.job_collection') as mock_collection:
        mock_collection.add.return_value = None

        id1 = add_to_job_chroma([0.1, 0.2], {"title": "Job 1"})
        id2 = add_to_job_chroma([0.3, 0.4], {"title": "Job 2"})

        # IDs should be different
        assert id1 != id2
        # Both should be valid UUIDs
        uuid.UUID(id1)
        uuid.UUID(id2)


def test_chroma_utils_imports():
    """Test that all required functions are available."""
    # This test ensures that the functions exist and can be imported
    assert callable(add_to_resume_chroma)
    assert callable(add_to_job_chroma)
    assert callable(search_resume_chroma)
    assert callable(get_all_jobs_from_chroma)
    assert callable(delete_resume_from_chroma)
    assert callable(delete_job_from_chroma)


if __name__ == "__main__":
    pytest.main()
