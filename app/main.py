from fastapi import FastAPI
from .database import Base, engine
from .models import User
from .routes import auth_routes, predict_routes
from .routes.predict_routes import fuel_model_service
from fastapi.middleware.cors import CORSMiddleware


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fuel Blend Property Prediction API",
    version="1.0.0",
    description="API for predicting fuel blend properties using machine learning models"
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods, including OPTIONS
    allow_headers=["*"], # Allows all headers
)
# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(predict_routes.router, prefix="/api", tags=["Predictions"])

@app.get("/")
def root():
    return {
        "message": "Fuel Blend Property Prediction API",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "predict": "/api/predict/fuel"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": fuel_model_service.model_loaded}