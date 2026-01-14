import pytest
from unittest.mock import patch, MagicMock
from embedding_utils import generate_embedding


def test_generate_embedding_success():
    """Test generating embedding for valid text."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4]

        result = generate_embedding("This is a test sentence.")

        assert result == [0.1, 0.2, 0.3, 0.4]
        mock_model.encode.assert_called_once_with("This is a test sentence.")


def test_generate_embedding_multiple_sentences():
    """Test generating embedding for multiple sentences."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.5, 0.6, 0.7, 0.8]

        text = "First sentence. Second sentence. Third sentence."
        result = generate_embedding(text)

        assert result == [0.5, 0.6, 0.7, 0.8]
        mock_model.encode.assert_called_once_with(text)


def test_generate_embedding_empty_string():
    """Test generating embedding for empty string."""
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("")

    assert "Input text is empty or invalid" in str(exc_info.value)


def test_generate_embedding_whitespace_only():
    """Test generating embedding for whitespace-only string."""
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("   ")

    assert "Input text is empty or invalid" in str(exc_info.value)


def test_generate_embedding_newlines_only():
    """Test generating embedding for newline-only string."""
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("\n\n\n")

    assert "Input text is empty or invalid" in str(exc_info.value)


def test_generate_embedding_non_string_input():
    """Test generating embedding for non-string input."""
    with pytest.raises(ValueError) as exc_info:
        generate_embedding(None)

    assert "Input text is empty or invalid" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        generate_embedding(123)

    assert "Input text is empty or invalid" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        generate_embedding([])

    assert "Input text is empty or invalid" in str(exc_info.value)


def test_generate_embedding_special_characters():
    """Test generating embedding for text with special characters."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.9, 0.8, 0.7, 0.6]

        text = "Hello, world! @#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        result = generate_embedding(text)

        assert result == [0.9, 0.8, 0.7, 0.6]
        mock_model.encode.assert_called_once_with(text)


def test_generate_embedding_unicode_text():
    """Test generating embedding for Unicode text."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.1, 0.9, 0.2, 0.8]

        text = "Hello 世界 🌍 Привет"
        result = generate_embedding(text)

        assert result == [0.1, 0.9, 0.2, 0.8]
        mock_model.encode.assert_called_once_with(text)


def test_generate_embedding_long_text():
    """Test generating embedding for long text."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.3, 0.4, 0.5, 0.6]

        long_text = "A" * 1000  # Long text
        result = generate_embedding(long_text)

        assert result == [0.3, 0.4, 0.5, 0.6]
        mock_model.encode.assert_called_once_with(long_text)


def test_generate_embedding_consistency():
    """Test that the same input produces the same embedding."""
    with patch('embedding_utils.model') as mock_model:
        mock_model.encode.return_value = [0.1, 0.2, 0.3]

        text = "Consistent test sentence"
        result1 = generate_embedding(text)
        result2 = generate_embedding(text)

        assert result1 == result2
        assert mock_model.encode.call_count == 2


if __name__ == "__main__":
    pytest.main()
