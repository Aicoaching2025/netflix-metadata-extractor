"""
Tests for the Netflix Metadata Extractor.

Run with: pytest tests/test_extractor.py -v
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from src.schemas import ContentMetadata
from src.extractor import NetflixExtractor


# ==============================
# Unit Tests - Schema Validation
# ==============================

class TestContentMetadata:
    """Test Pydantic schema validation."""

    def test_valid_metadata(self):
        """Valid data should create a model instance."""
        data = {
            "genres": ["Drama", "Thriller"],
            "themes": ["survival"],
            "mood": "dark",
            "target_audience": "adults",
            "content_warnings": ["violence"]
        }
        metadata = ContentMetadata(**data)
        assert metadata.genres == ["Drama", "Thriller"]
        assert metadata.mood == "dark"

    def test_empty_warnings_default(self):
        """Content warnings should default to empty list."""
        data = {
            "genres": ["Comedy"],
            "themes": ["love"],
            "mood": "lighthearted",
            "target_audience": "teens",
        }
        metadata = ContentMetadata(**data)
        assert metadata.content_warnings == []

    def test_missing_required_field(self):
        """Missing required fields should raise ValidationError."""
        data = {
            "genres": ["Drama"],
            # missing themes, mood, target_audience
        }
        with pytest.raises(ValidationError):
            ContentMetadata(**data)

    def test_wrong_type_genres(self):
        """Genres should be a list, not a string."""
        data = {
            "genres": "Drama",  # should be a list
            "themes": ["love"],
            "mood": "dark",
            "target_audience": "adults",
        }
        with pytest.raises(ValidationError):
            ContentMetadata(**data)

    def test_model_dump(self):
        """Model should serialize to dict correctly."""
        metadata = ContentMetadata(
            genres=["Action"],
            themes=["justice"],
            mood="thrilling",
            target_audience="adults",
            content_warnings=["violence"]
        )
        data = metadata.model_dump()
        assert isinstance(data, dict)
        assert data["mood"] == "thrilling"


# ==============================
# Unit Tests - JSON Parsing
# ==============================

class TestJSONParsing:
    """Test JSON parsing and cleaning logic."""

    @pytest.fixture
    def extractor(self):
        """Create an extractor with a dummy API key."""
        return NetflixExtractor(api_key="test-key")

    def test_clean_json(self, extractor):
        """Clean JSON should parse correctly."""
        response = '{"genres": ["Drama"], "themes": ["love"], "mood": "dark", "target_audience": "adults", "content_warnings": []}'
        data = extractor._parse_response(response)
        assert data["genres"] == ["Drama"]

    def test_json_with_markdown_backticks(self, extractor):
        """JSON wrapped in markdown code blocks should be cleaned."""
        response = '```json\n{"genres": ["Drama"], "themes": ["love"], "mood": "dark", "target_audience": "adults", "content_warnings": []}\n```'
        data = extractor._parse_response(response)
        assert data["genres"] == ["Drama"]

    def test_json_with_whitespace(self, extractor):
        """JSON with extra whitespace should parse correctly."""
        response = '  \n  {"genres": ["Drama"], "themes": ["love"], "mood": "dark", "target_audience": "adults", "content_warnings": []}  \n  '
        data = extractor._parse_response(response)
        assert data["mood"] == "dark"

    def test_invalid_json(self, extractor):
        """Invalid JSON should raise ValueError."""
        response = "This is not JSON at all"
        with pytest.raises(ValueError, match="Invalid JSON"):
            extractor._parse_response(response)

    def test_partial_json(self, extractor):
        """Incomplete JSON should raise ValueError."""
        response = '{"genres": ["Drama"'
        with pytest.raises(ValueError, match="Invalid JSON"):
            extractor._parse_response(response)


# ==============================
# Unit Tests - Extract with Mock
# ==============================

class TestExtractWithMock:
    """Test extraction logic with mocked API calls."""

    def _mock_extractor(self, api_response: str):
        """Create an extractor with a mocked API call."""
        extractor = NetflixExtractor(api_key="test-key")
        extractor._call_api = MagicMock(return_value=api_response)
        return extractor

    def test_successful_extraction(self):
        """A valid API response should return success."""
        response = json.dumps({
            "genres": ["Drama", "Thriller"],
            "themes": ["survival"],
            "mood": "dark",
            "target_audience": "adults",
            "content_warnings": ["violence"]
        })
        extractor = self._mock_extractor(response)
        result = extractor.extract("Test description")

        assert result["success"] is True
        assert result["retries"] == 0
        assert result["metadata"].genres == ["Drama", "Thriller"]

    def test_retry_on_invalid_json(self):
        """Should retry when first response is invalid JSON."""
        valid_response = json.dumps({
            "genres": ["Comedy"],
            "themes": ["love"],
            "mood": "lighthearted",
            "target_audience": "teens",
            "content_warnings": []
        })

        extractor = NetflixExtractor(api_key="test-key")
        extractor._call_api = MagicMock(
            side_effect=["Not valid JSON", valid_response]
        )

        result = extractor.extract("A fun romantic comedy")
        assert result["success"] is True
        assert result["retries"] == 1

    def test_all_retries_fail(self):
        """Should return failure after max retries."""
        extractor = NetflixExtractor(api_key="test-key")
        extractor._call_api = MagicMock(return_value="Not JSON")

        result = extractor.extract("Test description")
        assert result["success"] is False
        assert result["error"] is not None


# ==============================
# Integration Tests
# ==============================
# These tests call the real Anthropic API.
# Set ANTHROPIC_API_KEY env var to run them.
# Skip with: pytest tests/test_extractor.py -v -k "not integration"

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
class TestIntegration:
    """Integration tests that call the real API."""

    @pytest.fixture
    def extractor(self):
        return NetflixExtractor(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def test_drama_extraction(self, extractor):
        """Test extraction of a dramatic description."""
        description = "In a future where the elite inhabit an island paradise far from the crowded slums, you get one chance to join the 3% saved from squalor."
        result = extractor.extract(description)

        assert result["success"] is True
        assert isinstance(result["metadata"], ContentMetadata)
        assert len(result["metadata"].genres) > 0
        assert result["metadata"].target_audience in ["kids", "teens", "adults", "family"]

    def test_horror_extraction(self, extractor):
        """Test extraction of a horror description."""
        description = "After an awful accident, a couple admitted to a grisly hospital are separated and must find each other to escape — before death finds them."
        result = extractor.extract(description)

        assert result["success"] is True
        assert any(g.lower() in ["horror", "thriller"] for g in result["metadata"].genres)

    def test_comedy_extraction(self, extractor):
        """Test extraction of a lighthearted description."""
        description = "A young couple navigating the ups and downs of living together discover that love means learning to compromise on everything from pizza toppings to whose family to visit for the holidays."
        result = extractor.extract(description)

        assert result["success"] is True
        assert result["metadata"].mood in ["lighthearted", "comedic", "heartwarming", "funny"]