from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data on startup
data = pd.read_csv("telemetry.csv")  # Replace with your actual file path

class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
async def get_metrics(req: MetricsRequest):
    result = {}
    filtered_data = data[data["region"].isin(req.regions)]

    for region in req.regions:
        region_data = filtered_data[filtered_data["region"] == region]
        if region_data.empty:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = region_data["latency_ms"]
        uptimes = region_data["uptime"]

        avg_latency = latencies.mean()
        p95_latency = np.percentile(latencies, 95)
        avg_uptime = uptimes.mean()
        breaches = (latencies > req.threshold_ms).sum()

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": int(breaches)
        }

    return result
