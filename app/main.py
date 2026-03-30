from datetime import UTC, datetime
from enum import StrEnum
from threading import Lock
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class CommerceModule(StrEnum):
    DIRECTORY = "directory"
    APPOINTMENTS = "appointments"
    RESERVATIONS = "reservations"
    PRODUCTS = "products"
    REVIEWS = "reviews"
    PAYMENTS = "payments"
    NOTIFICATIONS = "notifications"


class BusinessType(StrEnum):
    DOCTOR = "doctor"
    RESTAURANT = "restaurant"
    SALON = "salon"
    RETAIL_SHOP = "retail_shop"
    COACHING = "coaching"
    EVENT_PLANNER = "event_planner"
    HOME_SERVICE = "home_service"


class BusinessBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    business_type: BusinessType
    city: str = Field(min_length=2, max_length=80)
    address: str | None = Field(default=None, max_length=300)
    contact_phone: str | None = Field(default=None, max_length=30)
    rating: float = Field(default=0, ge=0, le=5)
    modules: list[CommerceModule] = Field(default_factory=list)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, min_length=2, max_length=80)
    address: str | None = Field(default=None, max_length=300)
    contact_phone: str | None = Field(default=None, max_length=30)
    rating: float | None = Field(default=None, ge=0, le=5)
    modules: list[CommerceModule] | None = None


class Business(BusinessBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class BusinessTypeInfo(BaseModel):
    key: BusinessType
    label: str
    supported_modules: list[CommerceModule]


class ReviewBase(BaseModel):
    business_id: UUID
    reviewer_name: str = Field(min_length=2, max_length=120)
    rating: float = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


class ReviewCreate(ReviewBase):
    pass


class Review(ReviewBase):
    id: UUID
    created_at: datetime


class InMemoryBusinessRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._businesses: dict[UUID, Business] = {}
        self._reviews: dict[UUID, Review] = {}
        self._seed()

    def _seed(self) -> None:
        now = utc_now()
        seeded = [
            Business(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                name="Arogya Family Clinic",
                business_type=BusinessType.DOCTOR,
                city="Pune",
                address="Karve Nagar, Pune",
                contact_phone="+91-9999999991",
                rating=4.6,
                modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
                created_at=now,
                updated_at=now,
            ),
            Business(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                name="Spice Garden Restaurant",
                business_type=BusinessType.RESTAURANT,
                city="Nashik",
                address="College Road, Nashik",
                contact_phone="+91-9999999992",
                rating=4.3,
                modules=[CommerceModule.DIRECTORY, CommerceModule.RESERVATIONS, CommerceModule.REVIEWS],
                created_at=now,
                updated_at=now,
            ),
            Business(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                name="Style Studio Salon",
                business_type=BusinessType.SALON,
                city="Mumbai",
                address="Andheri West, Mumbai",
                contact_phone="+91-9999999993",
                rating=4.5,
                modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
                created_at=now,
                updated_at=now,
            ),
            Business(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                name="Mahalaxmi Mart",
                business_type=BusinessType.RETAIL_SHOP,
                city="Kolhapur",
                address="Shahupuri, Kolhapur",
                contact_phone="+91-9999999994",
                rating=4.2,
                modules=[CommerceModule.DIRECTORY, CommerceModule.PRODUCTS, CommerceModule.REVIEWS],
                created_at=now,
                updated_at=now,
            ),
        ]

        for item in seeded:
            self._businesses[item.id] = item

        seeded_reviews = [
            Review(
                id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                business_id=UUID("11111111-1111-1111-1111-111111111111"),
                reviewer_name="Rahul Patil",
                rating=5,
                comment="Great consultation and friendly staff.",
                created_at=now,
            ),
            Review(
                id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                business_id=UUID("22222222-2222-2222-2222-222222222222"),
                reviewer_name="Sneha Kulkarni",
                rating=4,
                comment="Good food and quick service.",
                created_at=now,
            ),
            Review(
                id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                business_id=UUID("33333333-3333-3333-3333-333333333333"),
                reviewer_name="Vijay Shinde",
                rating=5,
                comment="Very professional and on-time appointment.",
                created_at=now,
            ),
        ]

        for review in seeded_reviews:
            self._reviews[review.id] = review

    def list_business_types(self) -> list[BusinessTypeInfo]:
        return [
            BusinessTypeInfo(
                key=BusinessType.DOCTOR,
                label="Doctor",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.RESTAURANT,
                label="Restaurant",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.RESERVATIONS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.SALON,
                label="Salon",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.RETAIL_SHOP,
                label="Retail Shop",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.PRODUCTS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.COACHING,
                label="Coaching",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.EVENT_PLANNER,
                label="Event Planner",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.RESERVATIONS, CommerceModule.REVIEWS],
            ),
            BusinessTypeInfo(
                key=BusinessType.HOME_SERVICE,
                label="Home Service",
                supported_modules=[CommerceModule.DIRECTORY, CommerceModule.APPOINTMENTS, CommerceModule.REVIEWS],
            ),
        ]

    def list_businesses(
        self,
        business_type: BusinessType | None = None,
        city: str | None = None,
        min_rating: float | None = None,
        module: CommerceModule | None = None,
    ) -> list[Business]:
        items = list(self._businesses.values())

        if business_type is not None:
            items = [item for item in items if item.business_type == business_type]

        if city:
            city_normalized = city.strip().lower()
            items = [item for item in items if item.city.lower() == city_normalized]

        if min_rating is not None:
            items = [item for item in items if item.rating >= min_rating]

        if module is not None:
            items = [item for item in items if module in item.modules]

        return sorted(items, key=lambda item: item.name)

    def get_business(self, business_id: UUID) -> Business | None:
        return self._businesses.get(business_id)

    def create_business(self, payload: BusinessCreate) -> Business:
        with self._lock:
            now = utc_now()
            created = Business(
                id=uuid4(),
                created_at=now,
                updated_at=now,
                **payload.model_dump(),
            )
            self._businesses[created.id] = created
            return created

    def update_business(self, business_id: UUID, payload: BusinessUpdate) -> Business | None:
        with self._lock:
            current = self.get_business(business_id)
            if current is None:
                return None

            patch_data = payload.model_dump(exclude_unset=True)
            updated = current.model_copy(update={**patch_data, "updated_at": utc_now()})
            self._businesses[business_id] = updated
            return updated

    def list_business_reviews(self, business_id: UUID) -> list[Review]:
        if business_id not in self._businesses:
            raise LookupError("Business not found.")

        items = [review for review in self._reviews.values() if review.business_id == business_id]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def create_review(self, payload: ReviewCreate) -> Review:
        with self._lock:
            business = self._businesses.get(payload.business_id)
            if business is None:
                raise LookupError("Business not found.")

            now = utc_now()
            review = Review(id=uuid4(), created_at=now, **payload.model_dump())
            self._reviews[review.id] = review

            business_reviews = [r.rating for r in self._reviews.values() if r.business_id == payload.business_id]
            updated_rating = round(sum(business_reviews) / len(business_reviews), 2)
            self._businesses[payload.business_id] = business.model_copy(
                update={"rating": updated_rating, "updated_at": now}
            )

            return review


repository = InMemoryBusinessRepository()

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


@app.get("/api/v1/business-types", response_model=list[BusinessTypeInfo], summary="List Business Types")
async def list_business_types() -> list[BusinessTypeInfo]:
    return repository.list_business_types()


@app.get("/api/v1/businesses", response_model=list[Business], summary="List Businesses")
async def list_businesses(
    business_type: BusinessType | None = None,
    city: str | None = Query(default=None, min_length=2),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    module: CommerceModule | None = None,
) -> list[Business]:
    return repository.list_businesses(
        business_type=business_type,
        city=city,
        min_rating=min_rating,
        module=module,
    )


@app.get("/api/v1/businesses/{business_id}", response_model=Business, summary="Get Business")
async def get_business(business_id: UUID) -> Business:
    business = repository.get_business(business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found.",
        )
    return business


@app.post(
    "/api/v1/businesses",
    response_model=Business,
    status_code=status.HTTP_201_CREATED,
    summary="Create Business",
)
async def create_business(payload: BusinessCreate) -> Business:
    return repository.create_business(payload)


@app.patch("/api/v1/businesses/{business_id}", response_model=Business, summary="Update Business")
async def update_business(business_id: UUID, payload: BusinessUpdate) -> Business:
    business = repository.update_business(business_id, payload)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found.",
        )
    return business


@app.get(
    "/api/v1/businesses/{business_id}/reviews",
    response_model=list[Review],
    summary="List Business Reviews",
)
async def list_business_reviews(business_id: UUID) -> list[Review]:
    try:
        return repository.list_business_reviews(business_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/reviews",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    summary="Create Review",
)
async def create_review(payload: ReviewCreate) -> Review:
    try:
        return repository.create_review(payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
