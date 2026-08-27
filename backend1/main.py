from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

from disaster_pipeline import run_disaster_pipeline


class DisasterInput(BaseModel):
    mode: Literal["live", "simulation"] = "simulation"

    # Existing backend inputs
    rainfall_mm: float | None = Field(default=None, ge=0)
    duration_hours: float | None = Field(default=None, ge=0)
    water_level_m: float | None = Field(default=None, ge=0)

    # ML inputs
    rainfall_1h_mm: float | None = Field(default=None, ge=0)
    rainfall_3h_mm: float | None = Field(default=None, ge=0)
    rainfall_6h_mm: float | None = Field(default=None, ge=0)
    rainfall_12h_mm: float | None = Field(default=None, ge=0)
    rainfall_24h_mm: float | None = Field(default=None, ge=0)


app = FastAPI(
    title="Cascading Disaster Intelligence Platform"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Disaster Intelligence API is running"
    }


@app.post("/api/disaster/analyze")
def analyze_disaster(data: DisasterInput):

    # SIMULATION MODE
    if data.mode == "simulation":

        if (
            data.rainfall_mm is None
            or data.duration_hours is None
            or data.water_level_m is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Simulation mode requires rainfall, duration and water level."
            )

        return run_disaster_pipeline(
    rainfall_mm=data.rainfall_mm,
    duration_hours=data.duration_hours,
    water_level_m=data.water_level_m,
    rainfall_1h_mm=data.rainfall_1h_mm,
    rainfall_3h_mm=data.rainfall_3h_mm,
    rainfall_6h_mm=data.rainfall_6h_mm,
    rainfall_12h_mm=data.rainfall_12h_mm,
    rainfall_24h_mm=data.rainfall_24h_mm,
)
    

    # LIVE MODE - temporary fallback
    return run_disaster_pipeline(
        rainfall_mm=180,
        duration_hours=4,
        water_level_m=8,
    )