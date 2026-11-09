import os
import httpx
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

VGENV_API_KEY = os.environ.get("VGENV_API_KEY")
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN")


@app.get("/")
def home():
    return {"status": "VGenV server is running"}


@app.post("/videos")
async def create_video(
    data: dict,
    authorization: str = Header(None),
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    if not SERVICE_TOKEN or authorization != f"Bearer {SERVICE_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not VGENV_API_KEY:
        raise HTTPException(status_code=500, detail="VGenV API key is not configured")

    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    headers = {
        "Authorization": f"Bearer {VGENV_API_KEY}",
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.vgenv.com/v1/videos",
            headers=headers,
            json=data
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()
