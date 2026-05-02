from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    provider: str


class SkinPredictionResponse(BaseModel):
    prediction: str
    confidence: float
    description: str
    recommended_action: str


class StatusResponse(BaseModel):
    status: str
    project: str
