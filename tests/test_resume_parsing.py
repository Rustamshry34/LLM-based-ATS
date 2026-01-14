import pytest
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
from resume_parsing import parse_resume_with_llm


def test_parse_resume_with_valid_pdf():
    """Test parsing a valid PDF resume."""
    with patch('resume_parsing.agent') as mock_agent:
        mock_agent.extract.return_value = MagicMock()
        mock_agent.extract.return_value.data = {
            "experience": "5 years in software development",
            "education": "BSc Computer Science",
            "skills": ["Python", "JavaScript", "SQL"]
        }

        with patch('resume_parsing.generate_embedding') as mock_embedding:
            mock_embedding.return_value = [0.1, 0.2, 0.3]

            with patch('resume_parsing.add_to_resume_chroma') as mock_add_to_chroma:
                mock_add_to_chroma.return_value = "test-unique-id"

                pdf_content = b"%PDF-1.4 test pdf content"
                result, embedding = parse_resume_with_llm(pdf_content, "John Doe", "New York", "pdf")

                assert result["message"] == "Resume parsed successfully"
                assert result["unique_id"] == "test-unique-id"
                assert embedding is not None


def test_parse_resume_with_valid_docx():
    """Test parsing a valid DOCX resume."""
    with patch('resume_parsing.agent') as mock_agent:
        mock_agent.extract.return_value = MagicMock()
        mock_agent.extract.return_value.data = {
            "experience": "3 years in marketing",
            "education": "MBA Marketing",
            "skills": ["SEO", "Content Writing", "Analytics"]
        }

        with patch('resume_parsing.generate_embedding') as mock_embedding:
            mock_embedding.return_value = [0.4, 0.5, 0.6]

            with patch('resume_parsing.add_to_resume_chroma') as mock_add_to_chroma:
                mock_add_to_chroma.return_value = "test-unique-id"

                docx_content = b"PK\x03\x04 test docx content"
                result, embedding = parse_resume_with_llm(docx_content, "Jane Smith", "London", "docx")

                assert result["message"] == "Resume parsed successfully"
                assert result["unique_id"] == "test-unique-id"
                assert embedding is not None


def test_parse_resume_unsupported_file_type():
    """Test parsing with unsupported file type."""
    with patch('resume_parsing.agent'):
        result, embedding = parse_resume_with_llm(b"content", "John Doe", "New York", "txt")

        assert "error" in result
        assert "Unsupported file type" in result["error"]
        assert embedding is None


def test_parse_resume_no_data_extracted():
    """Test parsing when no data is extracted."""
    with patch('resume_parsing.agent') as mock_agent:
        mock_agent.extract.return_value = MagicMock()
        mock_agent.extract.return_value.data = {}  # No data extracted

        result, embedding = parse_resume_with_llm(b"%PDF-1.4 test", "John Doe", "New York", "pdf")

        assert "error" in result
        assert "No data extracted" in result["error"]
        assert embedding is None


def test_parse_resume_extraction_failure():
    """Test parsing when extraction fails."""
    with patch('resume_parsing.agent') as mock_agent:
        mock_agent.extract.side_effect = Exception("Extraction failed")

        result, embedding = parse_resume_with_llm(b"%PDF-1.4 test", "John Doe", "New York", "pdf")

        assert "error" in result
        assert "LlamaExtract failed" in result["error"]
        assert embedding is None


@patch('builtins.open', new_callable=mock_open)
@patch('tempfile.NamedTemporaryFile')
@patch('os.remove')
def test_parse_resume_temp_file_handling(mock_remove, mock_temp_file, mock_open_func):
    """Test temporary file creation and cleanup during resume parsing."""
    mock_temp_file.return_value.__enter__.return_value.name = '/tmp/temp_file.pdf'
    mock_temp_file.return_value.__enter__.return_value.write = lambda x: None

    with patch('resume_parsing.agent') as mock_agent:
        mock_agent.extract.return_value = MagicMock()
        mock_agent.extract.return_value.data = {
            "experience": "2 years in design",
            "education": "BFA Design",
            "skills": ["Photoshop", "Illustrator", "Figma"]
        }

        with patch('resume_parsing.generate_embedding') as mock_embedding:
            mock_embedding.return_value = [0.7, 0.8, 0.9]

            with patch('resume_parsing.add_to_resume_chroma') as mock_add_to_chroma:
                mock_add_to_chroma.return_value = "test-unique-id"

                pdf_content = b"%PDF-1.4 test pdf content"
                result, embedding = parse_resume_with_llm(pdf_content, "Alice Johnson", "Paris", "pdf")

                # Verify that the temporary file was created and removed
                mock_temp_file.assert_called()
                mock_remove.assert_called_once()


if __name__ == "__main__":
    pytest.main()
