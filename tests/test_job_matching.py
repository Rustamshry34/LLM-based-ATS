import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from job_matching import calculate_ats_score


def test_calculate_ats_score_success():
    """Test successful calculation of ATS scores."""
    job_embedding = np.array([0.1, 0.2, 0.3, 0.4])

    # Mock the search results
    mock_search_results = {
        'ids': [['candidate1', 'candidate2']],
        'embeddings': [[[0.15, 0.25, 0.35, 0.45], [0.05, 0.15, 0.25, 0.35]]],
        'metadatas': [[{'name': 'John Doe'}, {'name': 'Jane Smith'}]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        # Should return matched candidates sorted by score
        assert len(result) == 2
        assert result[0]['candidate_id'] == 'candidate1'
        assert result[1]['candidate_id'] == 'candidate2'
        # Scores should be between 0 and 1 (cosine similarity)
        assert 0 <= result[0]['score'] <= 1
        assert 0 <= result[1]['score'] <= 1
        assert result[0]['score'] >= result[1]['score']  # Should be sorted in descending order


def test_calculate_ats_score_single_candidate():
    """Test calculation with a single candidate."""
    job_embedding = np.array([0.5, 0.6, 0.7])

    mock_search_results = {
        'ids': [['candidate1']],
        'embeddings': [[[0.55, 0.65, 0.75]]],
        'metadatas': [[{'name': 'John Doe', 'skills': ['Python']}]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        assert len(result) == 1
        assert result[0]['candidate_id'] == 'candidate1'
        assert 'metadata' in result[0]
        assert result[0]['metadata']['name'] == 'John Doe'


def test_calculate_ats_score_no_candidates_found():
    """Test when no candidates are found."""
    job_embedding = np.array([0.1, 0.2, 0.3])

    mock_search_results = {
        'ids': [[]],
        'embeddings': [[]],
        'metadatas': [[]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        assert len(result) == 0


def test_calculate_ats_score_high_similarity():
    """Test with embeddings that have high similarity."""
    job_embedding = np.array([1.0, 1.0, 1.0])

    # Very similar candidate embedding
    mock_search_results = {
        'ids': [['candidate1']],
        'embeddings': [[[0.99, 0.99, 0.99]]],
        'metadatas': [[{'name': 'Top Candidate'}]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        assert len(result) == 1
        # Score should be close to 1 for very similar embeddings
        assert result[0]['score'] > 0.95


def test_calculate_ats_score_low_similarity():
    """Test with embeddings that have low similarity."""
    job_embedding = np.array([1.0, 1.0, 1.0])

    # Very different candidate embedding
    mock_search_results = {
        'ids': [['candidate1']],
        'embeddings': [[[-1.0, -1.0, -1.0]]],
        'metadatas': [[{'name': 'Low Match'}]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        assert len(result) == 1
        # Score should be lower for dissimilar embeddings
        assert result[0]['score'] < 0.5


def test_calculate_ats_score_exception_handling():
    """Test exception handling in calculate_ats_score."""
    job_embedding = np.array([0.1, 0.2, 0.3])

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.side_effect = Exception("Database connection failed")

        # Should raise the exception
        with pytest.raises(Exception):
            calculate_ats_score(job_embedding)


def test_calculate_ats_score_different_dimensions():
    """Test with embeddings of different dimensions."""
    job_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    mock_search_results = {
        'ids': [['candidate1']],
        'embeddings': [[[0.15, 0.25, 0.35, 0.45, 0.55]]],
        'metadatas': [[{'name': 'Test Candidate'}]]
    }

    with patch('job_matching.search_resume_chroma') as mock_search:
        mock_search.return_value = mock_search_results

        result = calculate_ats_score(job_embedding)

        assert len(result) == 1
        assert result[0]['candidate_id'] == 'candidate1'
        assert 0 <= result[0]['score'] <= 1


if __name__ == "__main__":
    pytest.main()
