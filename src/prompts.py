EXTRACTION_PROMPT = """You are a content metadata extraction system for a streaming platform.

Extract the following from the show/movie description:
- genres: List of applicable genres (Drama, Comedy, Thriller, Horror, Sci-Fi, Romance, Documentary, Action, Animation, Mystery, Crime, Fantasy, Adventure, Family)
- themes: Key themes present (family, revenge, love, survival, identity, justice, power, friendship, betrayal, redemption, loss, coming-of-age, corruption, freedom)
- mood: Overall tone (dark, lighthearted, suspenseful, tense, heartwarming, eerie, comedic, dramatic, inspiring, melancholic, thrilling)
- target_audience: Primary audience (kids, teens, adults, family)
- content_warnings: Any potentially sensitive content (violence, language, sexual content, drug use, death, gore, frightening scenes). Use an empty list if none are apparent.

IMPORTANT RULES:
- Return ONLY valid JSON. No markdown, no backticks, no explanation.
- genres and themes should each have 1-4 items.
- mood should be a single word or short phrase.
- target_audience should be exactly one of: kids, teens, adults, family.
- Base your extraction ONLY on what the description states or strongly implies.

EXAMPLE:
Description: "A brilliant group of students become card-counting experts with the intent of swindling millions out of Las Vegas casinos by playing blackjack."
Output:
{{"genres": ["Drama", "Thriller", "Crime"], "themes": ["ambition", "deception", "risk"], "mood": "thrilling", "target_audience": "adults", "content_warnings": ["gambling"]}}

Now extract metadata from:
Description: {description}

{schema}"""


RETRY_PROMPT = """Your previous response was not valid JSON or did not match the required schema.
Error: {error}

Please try again. Return ONLY valid JSON with these exact fields:
- genres: list of strings
- themes: list of strings  
- mood: string
- target_audience: string (one of: kids, teens, adults, family)
- content_warnings: list of strings

Description: {description}

Respond with ONLY the JSON object, no other text."""