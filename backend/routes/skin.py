from fastapi import APIRouter, File, HTTPException, UploadFile

from models.schemas import SkinPredictionResponse
from services.model_service import predict_skin_disease


router = APIRouter(tags=["skin"])


@router.post("/predict-skin", response_model=SkinPredictionResponse)
async def predict_skin(image: UploadFile = File(...)) -> SkinPredictionResponse:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported.")

    payload = await image.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    try:
        prediction = predict_skin_disease(payload)
        return SkinPredictionResponse(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
