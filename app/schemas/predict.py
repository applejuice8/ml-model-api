from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    X_data: list[str] = Field(
        ...,
        min_length=1,
        alias='X-data'
    )

class PredictResponse(BaseModel):
    prediction: list[int] = Field(
        ...,
        example=[0.1, 0.4, 0.5]
    )

