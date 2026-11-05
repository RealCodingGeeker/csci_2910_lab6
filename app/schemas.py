from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArtworkBase(BaseModel):
    title: str = Field(min_length=1, description="The title of the work")
    artist: str = Field(min_length=1, description="The artist who made it")
    year: int = Field(
        description="Year the work was made (the start year, for works made over several years)"
    )
    medium: str = Field(description='What it is made of, e.g. "Oil on canvas"')
    museum: str = Field(description="The museum that holds it")
    image_url: str = Field(description="URL to an image of the work")

    @field_validator("year")
    @classmethod
    def year_not_in_future(cls, value: int) -> int:
        if value > date.today().year:
            raise ValueError("year cannot be in the future")
        return value


class ArtworkCreate(ArtworkBase):
    """Body of a POST request. No `id`: the database assigns it."""


class ArtworkUpdate(ArtworkBase):
    """Body of a PUT request. An update replaces every field."""


class ArtworkResponse(ArtworkBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
