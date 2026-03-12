from fastapi import FastAPI, Depends, HTTPException, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import os

from app.database import get_db, init_db
from app.models import (
    Business, BusinessCreate, BusinessUpdate, BusinessResponse,
    BusinessListResponse, BUSINESS_CATEGORIES, VerificationStatus
)

init_db()

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

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mul-super-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _get_user_id(authorization: Optional[str]) -> Optional[int]:
    """Extract user_id from bearer token; returns None if missing/invalid."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    try:
        payload = jwt.decode(parts[1], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload.get("sub", 0)) or None
    except jwt.InvalidTokenError:
        return None


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/", summary="Business Service Root")
async def root() -> dict:
    return {"message": "MUL Business Service is running"}


@app.get("/health", summary="Health Check")
async def health() -> dict:
    return {"status": "ok", "service": "business-service"}


@app.get("/api/v1/business-categories", summary="List Business Categories")
async def list_categories() -> dict:
    return {"categories": BUSINESS_CATEGORIES}


@app.get("/api/v1/businesses", summary="List Businesses", response_model=BusinessListResponse)
async def list_businesses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    db: Session = Depends(get_db),
) -> BusinessListResponse:
    query = db.query(Business).filter(Business.is_active == True)

    if category:
        query = query.filter(Business.category == category.lower())
    if city:
        query = query.filter(Business.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            Business.name.ilike(f"%{search}%") | Business.description.ilike(f"%{search}%")
        )
    if verified_only:
        query = query.filter(Business.verification_status == VerificationStatus.VERIFIED)

    total = query.count()
    items = query.order_by(Business.rating.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return BusinessListResponse(total=total, page=page, page_size=page_size, items=items)


@app.get("/api/v1/businesses/{business_id}", summary="Get Business", response_model=BusinessResponse)
async def get_business(business_id: int, db: Session = Depends(get_db)) -> BusinessResponse:
    business = db.query(Business).filter(Business.id == business_id, Business.is_active == True).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@app.post("/api/v1/businesses", summary="Create Business", response_model=BusinessResponse, status_code=201)
async def create_business(
    data: BusinessCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> BusinessResponse:
    user_id = _get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    business = Business(
        **data.model_dump(),
        owner_id=user_id,
        category=data.category.lower()
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@app.patch("/api/v1/businesses/{business_id}", summary="Update Business", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    data: BusinessUpdate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> BusinessResponse:
    user_id = _get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this business")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "category" and value:
            value = value.lower()
        setattr(business, field, value)

    db.commit()
    db.refresh(business)
    return business


@app.patch("/api/v1/businesses/{business_id}/verify", summary="Verify Business (Admin)")
async def verify_business(
    business_id: int,
    action: str = Query(..., pattern="^(approve|reject)$"),
    db: Session = Depends(get_db),
) -> dict:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    business.verification_status = (
        VerificationStatus.VERIFIED if action == "approve" else VerificationStatus.REJECTED
    )
    db.commit()
    return {"message": f"Business {business.name} {action}d successfully", "status": business.verification_status}


@app.delete("/api/v1/businesses/{business_id}", summary="Deactivate Business", status_code=204)
async def deactivate_business(
    business_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_id = _get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    business.is_active = False
    db.commit()
