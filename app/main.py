from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MUL Business Service",
    version="1.0.0",
    description="Business directory, profiles, and verification",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Business Service Root")
async def root() -> dict[str, str]:
    return {"message": "MUL Business Service is running"}


@app.get("/health", summary="Health Check")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "business-service"}
