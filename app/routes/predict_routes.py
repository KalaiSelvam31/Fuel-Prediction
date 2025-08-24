from fastapi import APIRouter, Depends, HTTPException
from ..schemas import FuelPredictionInput, FuelPredictionResponse
from ..auth import get_current_user
from ..models import User
from ..ml_service import FuelModelService
import numpy as np

router = APIRouter()
fuel_model_service = FuelModelService()


@router.on_event("startup")
async def startup_event():
    await fuel_model_service.load_model()


@router.post("/predict/fuel", response_model=FuelPredictionResponse)
async def predict_fuel_properties(
        input_data: FuelPredictionInput,
        current_user: User = Depends(get_current_user)
):
    """
    Predict fuel blend properties from input features.

    Accepts either CSV format (with header row) or JSON format.
    Expected input features: Component fractions and properties as defined in the trained model.
    """
    try:
        predictions = await fuel_model_service.predict(
            input_data.data,
            input_data.data_type
        )

        return FuelPredictionResponse(
            prediction=predictions,
            status="success",
            message="Fuel properties predicted successfully",
            model_metrics={
                "rmse": 0.2488,
                "overall_r2": 0.94,
                "input_features_count": len(fuel_model_service.input_cols),
                "output_properties_count": len(fuel_model_service.output_cols)
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))