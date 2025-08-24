import numpy as np
import joblib
import asyncio
from pathlib import Path

class FuelModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.input_cols = None
        self.output_cols = None
        self.model_loaded = False
    
    async def load_model(self):
        """Load the trained model and preprocessing objects"""
        try:
            # Load all required files
            self.model = joblib.load('app/models/fuel_model.pkl')
            self.scaler = joblib.load('app/models/scaler.pkl')
            self.input_cols = joblib.load('app/models/input_cols.pkl')
            self.output_cols = joblib.load('app/models/output_cols.pkl')
            
            self.model_loaded = True
            print("✅ Fuel prediction model loaded successfully")
            print(f"   Input features: {len(self.input_cols)}")
            print(f"   Output properties: {len(self.output_cols)}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_loaded = False
    
    async def predict(self, input_data: list):
        """Make predictions using the trained model"""
        if not self.model_loaded:
            raise Exception("Fuel prediction model not loaded")
        
        try:
            # Convert input to numpy array
            input_array = np.array(input_data).reshape(1, -1)
            
            # Validate input length
            if len(input_data) != len(self.input_cols):
                expected = len(self.input_cols)
                received = len(input_data)
                raise ValueError(f"Expected {expected} features, got {received}")
            
            # Scale the input
            scaled_input = self.scaler.transform(input_array)
            
            # Make prediction
            prediction = self.model.predict(scaled_input)
            
            return {
                "blend_properties": prediction[0].tolist(),
                "rmse": 0.2488,
                "overall_r2": 0.94,
                "property_names": self.output_cols
            }
            
        except Exception as e:
            raise Exception(f"Prediction error: {e}")