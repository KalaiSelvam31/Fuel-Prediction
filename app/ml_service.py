# Add this at the VERY TOP of ml_service.py - before any other imports
import sys
import os

# Numpy compatibility workaround for pickle files
try:
    import numpy as np
    # Workaround for numpy._core compatibility
    if not hasattr(np, '_core'):
        try:
            # For older numpy versions that use np.core
            np._core = np.core
        except AttributeError:
            # Create a minimal mock if needed
            class FakeCore:
                multiarray = None
                umath = None
                def __getattr__(self, name):
                    return None
            np._core = FakeCore()
except ImportError:
    print("Error: numpy is required but not installed")
    sys.exit(1)



import numpy as np
import joblib
import asyncio
import  pandas as pd
from io import StringIO
import json
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
            model_path = Path('app/models/fuel_model.pkl')
            scaler_path = Path('app/models/scaler.pkl')
            input_cols_path = Path('app/models/input_cols.pkl')
            output_cols_path = Path('app/models/output_cols.pkl')

            if not all([model_path.exists(), scaler_path.exists(),
                        input_cols_path.exists(), output_cols_path.exists()]):
                raise FileNotFoundError("One or more model files are missing")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.input_cols = joblib.load(input_cols_path)
            self.output_cols = joblib.load(output_cols_path)

            self.model_loaded = True
            print("✅ Fuel prediction model loaded successfully")
            print(f"   Input features: {len(self.input_cols)}")
            print(f"   Output properties: {len(self.output_cols)}")

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_loaded = False
            raise

    async def process_input_data(self, input_data: str, data_type: str):
        """Process input data from either CSV or JSON format"""
        try:
            if data_type == 'csv':
                # Parse CSV string
                df = pd.read_csv(StringIO(input_data))

                # Validate columns match expected input_cols
                if list(df.columns) != self.input_cols:
                    raise ValueError(
                        f"CSV columns don't match expected features. Expected: {self.input_cols}, Got: {list(df.columns)}")

                features = df.values

            elif data_type == 'json':
                # Parse JSON data
                if isinstance(input_data, str):
                    data = json.loads(input_data)
                else:
                    data = input_data

                # Convert to DataFrame to ensure proper structure
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])

                # Validate columns
                if list(df.columns) != self.input_cols:
                    raise ValueError(
                        f"JSON features don't match expected features. Expected: {self.input_cols}, Got: {list(df.columns)}")

                features = df.values
            else:
                raise ValueError(f"Unsupported data type: {data_type}")

            return features

        except Exception as e:
            raise Exception(f"Error processing input data: {str(e)}")

    async def predict(self, input_data: str, data_type: str):
        """Make predictions using the trained fuel model"""
        if not self.model_loaded:
            raise Exception("Fuel prediction model not loaded")

        try:
            # Process the input data
            features = await self.process_input_data(input_data, data_type)

            # Validate input length
            if features.shape[1] != len(self.input_cols):
                expected = len(self.input_cols)
                received = features.shape[1]
                raise ValueError(f"Expected {expected} features, got {received}")

            # Scale the input
            scaled_input = self.scaler.transform(features)

            # Make prediction
            predictions = self.model.predict(scaled_input)

            # Convert to list of dictionaries with property names
            results = []
            for i, pred_row in enumerate(predictions):
                property_dict = {}
                for j, prop_name in enumerate(self.output_cols):
                    property_dict[prop_name] = float(pred_row[j])
                results.append(property_dict)

            return results

        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}")