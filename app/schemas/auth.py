from pydantic import BaseModel, Field
from typing import Literal

class AuthRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        example='adam123'
    )
    password: str = Field(
        ...,
        min_length=3,
        max_length=20,
    )

class AuthResponse(BaseModel):
    status: str = Field(
        ...,
        Literal('success', 'failure')
    )
