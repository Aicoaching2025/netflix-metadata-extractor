import json
import re
import anthropic
from pydantic import ValidationError
from .schemas import ContentMetadata
from .prompts import EXTRACTION_PROMPT, RETRY_PROMPT


class NetflixExtractor:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = 2

    def _get_schema_string(self) -> str:
        """Generate a schema string from the Pydantic model."""
        schema = ContentMetadata.model_json_schema()
        return f"Required JSON schema: {json.dumps(schema, indent=2)}"

    def _call_api(self, prompt: str) -> str:
        """Make an API call to Claude and return the response text."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def _clean_json_response(self, response: str) -> str:
        """Strip markdown backticks and extra whitespace from the response."""
        # Remove markdown code blocks
        cleaned = re.sub(r"```json\s*", "", response)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()
        return cleaned

    def _parse_response(self, response: str) -> dict:
        """Parse the API response into a dictionary."""
        cleaned = self._clean_json_response(response)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}\nResponse was: {cleaned}")

    def _validate(self, data: dict) -> ContentMetadata:
        """Validate parsed data against the Pydantic schema."""
        return ContentMetadata(**data)

    def extract(self, description: str) -> dict:
        """
        Extract metadata from a description with retry logic.

        Returns a dict with:
            - metadata: ContentMetadata or None
            - raw_response: str (the raw API response)
            - retries: int (number of retries needed)
            - success: bool
            - error: str or None
        """
        schema_str = self._get_schema_string()
        prompt = EXTRACTION_PROMPT.format(
            description=description,
            schema=schema_str
        )

        last_error = None

        for attempt in range(1 + self.max_retries):
            try:
                # Use retry prompt on subsequent attempts
                if attempt > 0:
                    prompt = RETRY_PROMPT.format(
                        error=str(last_error),
                        description=description
                    )

                # Call API
                raw_response = self._call_api(prompt)

                # Parse JSON
                data = self._parse_response(raw_response)

                # Validate with Pydantic
                metadata = self._validate(data)

                return {
                    "metadata": metadata,
                    "raw_response": raw_response,
                    "retries": attempt,
                    "success": True,
                    "error": None
                }

            except (ValueError, ValidationError, json.JSONDecodeError) as e:
                last_error = e
                if attempt < self.max_retries:
                    print(f"  Attempt {attempt + 1} failed: {e}. Retrying...")
                continue

        return {
            "metadata": None,
            "raw_response": raw_response if "raw_response" in dir() else None,
            "retries": self.max_retries,
            "success": False,
            "error": str(last_error)
        }

    def extract_batch(self, descriptions: list[dict]) -> list[dict]:
        """
        Extract metadata from a list of items.

        Each item should have 'title' and 'description' keys.
        Returns a list of result dicts.
        """
        results = []
        for i, item in enumerate(descriptions):
            title = item.get("title", f"Item {i+1}")
            description = item.get("description", "")

            print(f"[{i+1}/{len(descriptions)}] Extracting: {title}...")
            result = self.extract(description)
            result["title"] = title
            result["description"] = description
            results.append(result)

            if result["success"]:
                print(f"  Success (retries: {result['retries']})")
            else:
                print(f"  FAILED: {result['error']}")

        return results