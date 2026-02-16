from pydantic import BaseModel, Field


class ContentMetadata(BaseModel):
    genres: list[str] = Field(
        description="List of genres, e.g., ['Drama', 'Thriller']"
    )
    themes: list[str] = Field(
        description="List of themes, e.g., ['family', 'redemption']"
    )
    mood: str = Field(
        description="Overall mood, e.g., 'dark', 'lighthearted', 'suspenseful'"
    )
    target_audience: str = Field(
        description="Intended audience, e.g., 'adults', 'teens', 'children'"
    )
    content_warnings: list[str] = Field(
        default=[],
        description="Content warnings, e.g., ['violence', 'language']"
    )