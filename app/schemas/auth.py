from pydantic import BaseModel, Field

class UsernamePassword(BaseModel):
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

class SignupRequest(UsernamePassword):
    pass

class LoginRequest(UsernamePassword):
    pass

class AuthResponse(BaseModel):
    api_key: str
