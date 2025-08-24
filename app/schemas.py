from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Union, Dict
from pydantic import Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Fuel Prediction Input Schema
class FuelPredictionInput(BaseModel):
    data: Union[str, List[Dict], Dict] = Field(
        ...,
        description="Input data as CSV string or JSON object/array. For CSV, include header row with feature names."
    )
    data_type: str = Field(
        ...,
        description="Type of input data: 'csv' or 'json'",
        pattern="^(csv|json)$"
    )

# Fuel Property Output Schema
class FuelPropertyOutput(BaseModel):
    name: str
    value: float
    unit: Optional[str] = None

class FuelPredictionOutput(BaseModel):
    properties: List[FuelPropertyOutput]
    rmse: float = 0.2488
    overall_r2: float = 0.94

class FuelPredictionResponse(BaseModel):
    prediction: List[Dict[str, float]]  # List of dictionaries with property: value pairs
    status: str
    message: str
    model_metrics: Optional[Dict] = None