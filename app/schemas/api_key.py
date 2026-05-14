from pydantic import BaseModel, Field

class APIKeyResponse(BaseModel):
    key: str = Field(
        ...,
        min_length=20
    )
