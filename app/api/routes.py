from fastapi import APIRouter, HTTPException, Depends, Response, Request, Query
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import bcrypt
import jwt
import stripe
import os
import logging
from app.utils.db import db, get_db

JWT_SECRET = os.environ.get("JWT_SECRET", "qmeal-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY", "sk_test_mock_key_for_development"
)
STRIPE_PUBLISHABLE_KEY = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY", "pk_test_mock_key_for_development"
)
stripe.api_key = STRIPE_SECRET_KEY
api_router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def get_now_utc():
    return datetime.now(timezone.utc)


def get_rest_id():
    return f"rest_{uuid.uuid4().hex[:12]}"


def get_item_id():
    return f"item_{uuid.uuid4().hex[:12]}"


def get_rev_id():
    return f"rev_{uuid.uuid4().hex[:12]}"


def get_promo_id():
    return f"promo_{uuid.uuid4().hex[:12]}"


def get_ord_id():
    return f"ord_{uuid.uuid4().hex[:12]}"


def get_fav_id():
    return f"fav_{uuid.uuid4().hex[:12]}"


def get_notif_id():
    return f"notif_{uuid.uuid4().hex[:12]}"


def get_del_id():
    return f"del_{uuid.uuid4().hex[:12]}"


def get_pay_id():
    return f"pay_{uuid.uuid4().hex[:12]}"


class User(BaseModel):
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    picture: Optional[str] = None
    push_token: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None
    created_at: datetime = Field(default_factory=get_now_utc)


class UserSession(BaseModel):
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=get_now_utc)


class RegisterRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    name: str


class LoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    picture: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None
    token: str


class UpdatePushTokenRequest(BaseModel):
    push_token: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class OperatingHours(BaseModel):
    open: str
    close: str
    is_closed: bool = False


class Restaurant(BaseModel):
    restaurant_id: str = Field(default_factory=get_rest_id)
    name: str
    description: str
    cuisine_type: str
    rating: float = 0.0
    review_count: int = 0
    price_level: int = 2
    image_url: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    delivery_time_min: int = 20
    delivery_time_max: int = 40
    delivery_fee: float = 2.99
    is_open: bool = True
    operating_hours: Optional[dict] = None
    created_at: datetime = Field(default_factory=get_now_utc)


class MenuItem(BaseModel):
    item_id: str = Field(default_factory=get_item_id)
    restaurant_id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False


class Review(BaseModel):
    review_id: str = Field(default_factory=get_rev_id)
    restaurant_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=get_now_utc)


class CartItem(BaseModel):
    item_id: str
    name: str
    price: float
    quantity: int
    restaurant_id: str


class Promotion(BaseModel):
    promo_id: str = Field(default_factory=get_promo_id)
    restaurant_id: str
    code: str
    discount_percentage: float
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_now_utc)


class Order(BaseModel):
    order_id: str = Field(default_factory=get_ord_id)
    user_id: str
    restaurant_id: str
    restaurant_name: str
    items: list[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    status: str = "pending"
    delivery_address: str
    payment_intent_id: Optional[str] = None
    payment_status: str = "pending"
    rider_id: Optional[str] = None
    created_at: datetime = Field(default_factory=get_now_utc)


class Favorite(BaseModel):
    favorite_id: str = Field(default_factory=get_fav_id)
    user_id: str
    restaurant_id: str
    created_at: datetime = Field(default_factory=get_now_utc)


class Notification(BaseModel):
    notification_id: str = Field(default_factory=get_notif_id)
    user_id: str
    title: str
    body: str
    data: Optional[dict] = None
    read: bool = False
    created_at: datetime = Field(default_factory=get_now_utc)


class Delivery(BaseModel):
    delivery_id: str = Field(default_factory=get_del_id)
    order_id: str
    rider_id: Optional[str] = None
    restaurant_id: str
    status: str = "pending"
    pickup_location: dict
    dropoff_location: dict
    delivery_fee: float
    tip: float = 0.0
    created_at: datetime = Field(default_factory=get_now_utc)
    accepted_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class Payout(BaseModel):
    payout_id: str = Field(default_factory=get_pay_id)
    user_id: str
    amount: float
    status: str = "pending"
    method: str = "bank_transfer"
    created_at: datetime = Field(default_factory=get_now_utc)
    processed_at: Optional[datetime] = None


class AdminSettings(BaseModel):
    id: str = "global"
    platform_commission_rate: float = 0.15
    base_delivery_fee: float = 2.99
    is_platform_active: bool = True
    updated_at: datetime = Field(default_factory=get_now_utc)


class CreateOrderRequest(BaseModel):
    restaurant_id: str
    restaurant_name: str
    items: list[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    delivery_address: str
    payment_method_id: Optional[str] = None


class CreateReviewRequest(BaseModel):
    restaurant_id: str
    rating: int
    comment: str


class CreatePaymentIntentRequest(BaseModel):
    amount: float
    currency: str = "usd"


class UpdateOrderStatusRequest(BaseModel):
    status: str


class RegisterOwnerRequest(BaseModel):
    email: str
    password: str
    name: str
    restaurant_name: str
    cuisine_type: str
    description: str
    address: str


class RegisterRiderRequest(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    vehicle_type: str = "bicycle"


class RegisterAdminRequest(BaseModel):
    email: str
    password: str
    name: str
    secret_key: str


class AddMenuItemRequest(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False


class UpdateMenuItemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_popular: Optional[bool] = None


class UpdateRestaurantRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    delivery_time_min: Optional[int] = None
    delivery_time_max: Optional[int] = None
    delivery_fee: Optional[float] = None
    is_open: Optional[bool] = None
    image_url: Optional[str] = None
    operating_hours: Optional[dict] = None


class PayoutRequest(BaseModel):
    amount: float
    method: str = "bank_transfer"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logging.exception("Unexpected error")
        return None
    except jwt.InvalidTokenError:
        logging.exception("Unexpected error")
        return None


async def get_token_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get("auth_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


async def get_current_user(request: Request) -> Optional[User]:
    token = await get_token_from_request(request)
    if not token:
        return None
    payload = decode_jwt_token(token)
    if not payload:
        return None
    user_doc = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
    if user_doc:
        return User(**user_doc)
    return None


async def require_auth(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_rider(request: Request) -> User:
    user = await require_auth(request)
    if user.role != "rider":
        raise HTTPException(status_code=403, detail="Rider access required")
    return user


async def require_admin(request: Request) -> User:
    user = await require_auth(request)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def send_push_notification(
    user_id: str, title: str, body: str, data: dict = None
):
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user or not user.get("push_token"):
        return False
    push_token = user["push_token"]
    notification = Notification(user_id=user_id, title=title, body=body, data=data)
    await db.notifications.insert_one(notification.dict())
    try:
        message = {
            "to": push_token,
            "title": title,
            "body": body,
            "data": data or {},
            "sound": "default",
        }
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                "https://exp.host/--/api/v2/push/send",
                json=message,
                headers={"Content-Type": "application/json"},
            )
            return response.status_code == 200
    except Exception as e:
        logging.exception("Unexpected error")
        return False


@api_router.post("/auth/register", response_model=AuthResponse)
async def register(request_data: RegisterRequest, response: Response):
    if not request_data.email and (not request_data.phone):
        raise HTTPException(status_code=400, detail="Email or phone number is required")
    query = {}
    if request_data.email:
        query["email"] = request_data.email.lower()
    if request_data.phone:
        query["phone"] = request_data.phone
    existing_user = await db.users.find_one(query, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User already exists with this email or phone"
        )
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = hash_password(request_data.password)
    user_doc = {
        "user_id": user_id,
        "email": request_data.email.lower() if request_data.email else None,
        "phone": request_data.phone,
        "name": request_data.name,
        "password_hash": hashed_password,
        "picture": None,
        "push_token": None,
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user_doc)
    token = create_jwt_token(user_id)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600,
    )
    return AuthResponse(
        user_id=user_id,
        email=request_data.email,
        phone=request_data.phone,
        name=request_data.name,
        role="customer",
        token=token,
    )


@api_router.post("/auth/login", response_model=AuthResponse)
async def login(request_data: LoginRequest, response: Response):
    if not request_data.email and (not request_data.phone):
        raise HTTPException(status_code=400, detail="Email or phone number is required")
    query = {}
    if request_data.email:
        query["email"] = request_data.email.lower()
    elif request_data.phone:
        query["phone"] = request_data.phone
    user_doc = await db.users.find_one(query, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(request_data.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token(user_doc["user_id"])
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600,
    )
    return AuthResponse(
        user_id=user_doc["user_id"],
        email=user_doc.get("email"),
        phone=user_doc.get("phone"),
        name=user_doc["name"],
        picture=user_doc.get("picture"),
        role=user_doc.get("role", "customer"),
        restaurant_id=user_doc.get("restaurant_id"),
        token=token,
    )


@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(require_auth)):
    return current_user


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    response.delete_cookie(key="auth_token", path="/")
    return {"message": "Logged out successfully"}


@api_router.post("/auth/push-token")
async def update_push_token(
    request_data: UpdatePushTokenRequest, current_user: User = Depends(require_auth)
):
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"push_token": request_data.push_token}},
    )
    return {"message": "Push token updated"}


@api_router.patch("/auth/profile")
async def update_profile(
    request_data: UpdateProfileRequest, current_user: User = Depends(require_auth)
):
    update_fields = {}
    if request_data.name is not None:
        update_fields["name"] = request_data.name
    if request_data.email is not None:
        existing = await db.users.find_one(
            {"email": request_data.email, "user_id": {"$ne": current_user.user_id}}
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        update_fields["email"] = request_data.email
    if request_data.phone is not None:
        update_fields["phone"] = request_data.phone
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.users.update_one(
        {"user_id": current_user.user_id}, {"$set": update_fields}
    )
    updated_user = await db.users.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "password": 0}
    )
    return updated_user


@api_router.post("/auth/register-owner", response_model=AuthResponse)
async def register_owner(request_data: RegisterOwnerRequest, response: Response):
    existing = await db.users.find_one({"email": request_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    restaurant_id = f"rest_{uuid.uuid4().hex[:12]}"
    restaurant = {
        "restaurant_id": restaurant_id,
        "name": request_data.restaurant_name,
        "description": request_data.description,
        "cuisine_type": request_data.cuisine_type,
        "rating": 0.0,
        "review_count": 0,
        "price_level": 2,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        "address": request_data.address,
        "latitude": 40.7128,
        "longitude": -74.006,
        "delivery_time_min": 25,
        "delivery_time_max": 45,
        "delivery_fee": 2.99,
        "is_open": True,
        "created_at": datetime.now(timezone.utc),
    }
    await db.restaurants.insert_one(restaurant)
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "name": request_data.name,
        "password_hash": hash_password(request_data.password),
        "role": "owner",
        "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user)
    token = create_jwt_token(user_id)
    return AuthResponse(
        user_id=user_id,
        email=request_data.email,
        name=request_data.name,
        role="owner",
        restaurant_id=restaurant_id,
        token=token,
    )


@api_router.post("/auth/register-rider", response_model=AuthResponse)
async def register_rider(request_data: RegisterRiderRequest, response: Response):
    existing = await db.users.find_one({"email": request_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "phone": request_data.phone,
        "name": request_data.name,
        "password_hash": hash_password(request_data.password),
        "role": "rider",
        "vehicle_type": request_data.vehicle_type,
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user)
    token = create_jwt_token(user_id)
    return AuthResponse(
        user_id=user_id,
        email=request_data.email,
        phone=request_data.phone,
        name=request_data.name,
        role="rider",
        token=token,
    )


@api_router.post("/auth/register-admin", response_model=AuthResponse)
async def register_admin(request_data: RegisterAdminRequest, response: Response):
    if request_data.secret_key != "qmeal_admin_secret_2024":
        raise HTTPException(status_code=403, detail="Invalid admin secret key")
    existing = await db.users.find_one({"email": request_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "name": request_data.name,
        "password_hash": hash_password(request_data.password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user)
    token = create_jwt_token(user_id)
    return AuthResponse(
        user_id=user_id,
        email=request_data.email,
        name=request_data.name,
        role="admin",
        token=token,
    )


@api_router.get("/restaurants", response_model=list[Restaurant])
async def get_restaurants(
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    price_level: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(
        default="rating", pattern="^(rating|delivery_time|price)$"
    ),
):
    query = {}
    if cuisine:
        query["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
    if min_rating:
        query["rating"] = {"$gte": min_rating}
    if price_level:
        query["price_level"] = price_level
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"cuisine_type": {"$regex": search, "$options": "i"}},
        ]
    sort_field = "rating"
    sort_order = -1
    if sort_by == "delivery_time":
        sort_field, sort_order = ("delivery_time_min", 1)
    elif sort_by == "price":
        sort_field, sort_order = ("price_level", 1)
    restaurants = (
        await db.restaurants.find(query, {"_id": 0})
        .sort(sort_field, sort_order)
        .to_list(100)
    )
    return [Restaurant(**r) for r in restaurants]


@api_router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    restaurant = await db.restaurants.find_one(
        {"restaurant_id": restaurant_id}, {"_id": 0}
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return Restaurant(**restaurant)


@api_router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
async def get_restaurant_menu(restaurant_id: str):
    items = await db.menu_items.find(
        {"restaurant_id": restaurant_id, "is_available": True}, {"_id": 0}
    ).to_list(100)
    return [MenuItem(**item) for item in items]


@api_router.get("/restaurants/{restaurant_id}/reviews", response_model=list[Review])
async def get_restaurant_reviews(restaurant_id: str):
    reviews = (
        await db.reviews.find({"restaurant_id": restaurant_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(50)
    )
    return [Review(**r) for r in reviews]


@api_router.get("/cuisines")
async def get_cuisines():
    return {"cuisines": await db.restaurants.distinct("cuisine_type")}


@api_router.get("/favorites", response_model=list[Restaurant])
async def get_favorites(current_user: User = Depends(require_auth)):
    favorites = await db.favorites.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).to_list(100)
    restaurant_ids = [f["restaurant_id"] for f in favorites]
    if not restaurant_ids:
        return []
    restaurants = await db.restaurants.find(
        {"restaurant_id": {"$in": restaurant_ids}}, {"_id": 0}
    ).to_list(100)
    return [Restaurant(**r) for r in restaurants]


@api_router.post("/favorites/{restaurant_id}")
async def add_favorite(restaurant_id: str, current_user: User = Depends(require_auth)):
    restaurant = await db.restaurants.find_one({"restaurant_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    existing = await db.favorites.find_one(
        {"user_id": current_user.user_id, "restaurant_id": restaurant_id}
    )
    if existing:
        return {"message": "Already in favorites"}
    favorite = Favorite(user_id=current_user.user_id, restaurant_id=restaurant_id)
    await db.favorites.insert_one(favorite.dict())
    return {"message": "Added to favorites", "favorite_id": favorite.favorite_id}


@api_router.delete("/favorites/{restaurant_id}")
async def remove_favorite(
    restaurant_id: str, current_user: User = Depends(require_auth)
):
    result = await db.favorites.delete_one(
        {"user_id": current_user.user_id, "restaurant_id": restaurant_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


@api_router.get("/favorites/check/{restaurant_id}")
async def check_favorite(
    restaurant_id: str, current_user: User = Depends(require_auth)
):
    existing = await db.favorites.find_one(
        {"user_id": current_user.user_id, "restaurant_id": restaurant_id}
    )
    return {"is_favorite": existing is not None}


@api_router.get("/orders", response_model=list[Order])
async def get_user_orders(current_user: User = Depends(require_auth)):
    orders = (
        await db.orders.find({"user_id": current_user.user_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(50)
    )
    return [Order(**o) for o in orders]


@api_router.post("/orders", response_model=Order)
async def create_order(
    order_data: CreateOrderRequest, current_user: User = Depends(require_auth)
):
    order = Order(
        user_id=current_user.user_id,
        restaurant_id=order_data.restaurant_id,
        restaurant_name=order_data.restaurant_name,
        items=[CartItem(**item.dict()) for item in order_data.items],
        subtotal=order_data.subtotal,
        delivery_fee=order_data.delivery_fee,
        total=order_data.total,
        delivery_address=order_data.delivery_address,
        status="confirmed",
        payment_status="completed" if order_data.payment_method_id else "pending",
    )
    await db.orders.insert_one(order.dict())
    return order


@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user: User = Depends(require_auth)):
    order = await db.orders.find_one(
        {"order_id": order_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@api_router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_auth),
):
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"status": status_data.status}}
    )
    return {"message": "Status updated", "status": status_data.status}


@api_router.post("/payments/create-intent")
async def create_payment_intent(
    request_data: CreatePaymentIntentRequest, current_user: User = Depends(require_auth)
):
    return {
        "client_secret": "mock",
        "payment_intent_id": "mock",
        "publishable_key": "mock",
    }


@api_router.get("/payments/config")
async def get_payment_config():
    return {"publishable_key": "mock", "is_mock": True}


@api_router.post("/reviews", response_model=Review)
async def create_review(
    review_data: CreateReviewRequest, current_user: User = Depends(require_auth)
):
    review = Review(
        restaurant_id=review_data.restaurant_id,
        user_id=current_user.user_id,
        user_name=current_user.name,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    await db.reviews.insert_one(review.dict())
    return review


@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(require_auth)):
    return (
        await db.notifications.find({"user_id": current_user.user_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(50)
    )


@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str, current_user: User = Depends(require_auth)
):
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user.user_id},
        {"$set": {"read": True}},
    )
    return {"message": "Notification marked as read"}


@api_router.post("/notifications/read-all")
async def mark_all_notifications_read(current_user: User = Depends(require_auth)):
    await db.notifications.update_many(
        {"user_id": current_user.user_id}, {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}


async def require_owner(request: Request) -> User:
    user = await get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return user


@api_router.get("/owner/dashboard")
async def owner_dashboard(current_user: User = Depends(require_owner)):
    return {"restaurant": {}, "stats": {}}


@api_router.get("/owner/orders")
async def owner_get_orders(
    status: Optional[str] = None, current_user: User = Depends(require_owner)
):
    query = {"restaurant_id": current_user.restaurant_id}
    if status:
        query["status"] = status
    return await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)


@api_router.patch("/owner/orders/{order_id}/status")
async def owner_update_order_status(
    order_id: str,
    request_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_owner),
):
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"status": request_data.status}}
    )
    return {"message": "Order status updated"}


@api_router.get("/owner/menu")
async def owner_get_menu(current_user: User = Depends(require_owner)):
    return await db.menu_items.find(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    ).to_list(200)


@api_router.post("/owner/menu")
async def owner_add_menu_item(
    request_data: AddMenuItemRequest, current_user: User = Depends(require_owner)
):
    return {}


@api_router.patch("/owner/menu/{item_id}")
async def owner_update_menu_item(
    item_id: str,
    request_data: UpdateMenuItemRequest,
    current_user: User = Depends(require_owner),
):
    return {}


@api_router.delete("/owner/menu/{item_id}")
async def owner_delete_menu_item(
    item_id: str, current_user: User = Depends(require_owner)
):
    return {"message": "Menu item deleted"}


@api_router.get("/owner/promotions")
async def owner_get_promotions(current_user: User = Depends(require_owner)):
    return await db.promotions.find(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    ).to_list(50)


@api_router.post("/owner/promotions")
async def owner_create_promotion(
    request_data: dict, current_user: User = Depends(require_owner)
):
    return {}


@api_router.delete("/owner/promotions/{promo_id}")
async def owner_delete_promotion(
    promo_id: str, current_user: User = Depends(require_owner)
):
    return {"message": "Promotion deleted"}


@api_router.get("/owner/payouts")
async def owner_get_payouts(current_user: User = Depends(require_owner)):
    return {"available_balance": 0, "history": []}


@api_router.post("/owner/payouts/request")
async def owner_request_payout(
    request_data: PayoutRequest, current_user: User = Depends(require_owner)
):
    return {"message": "Payout requested"}


@api_router.get("/owner/restaurant")
async def owner_get_restaurant(current_user: User = Depends(require_owner)):
    return await db.restaurants.find_one(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    )


@api_router.patch("/owner/restaurant")
async def owner_update_restaurant(
    request_data: UpdateRestaurantRequest, current_user: User = Depends(require_owner)
):
    return {}


@api_router.post("/seed")
async def seed_database():
    return {"message": "Database seeded"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@api_router.get("/admin/dashboard")
async def admin_dashboard(current_user: User = Depends(require_admin)):
    return {
        "total_users": 0,
        "total_restaurants": 0,
        "total_orders": 0,
        "total_revenue": 0,
    }


@api_router.get("/admin/restaurants")
async def admin_list_restaurants(
    skip: int = 0, limit: int = 20, current_user: User = Depends(require_admin)
):
    return (
        await db.restaurants.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    )


@api_router.get("/admin/users")
async def admin_list_users(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
):
    return await db.users.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)


@api_router.patch("/admin/users/{user_id}")
async def admin_update_user(
    user_id: str, request_data: dict, current_user: User = Depends(require_admin)
):
    return {"message": "User updated successfully"}


@api_router.patch("/admin/restaurants/{restaurant_id}")
async def admin_update_restaurant(
    restaurant_id: str, request_data: dict, current_user: User = Depends(require_admin)
):
    return {"message": "Restaurant updated successfully"}


@api_router.get("/rider/available-orders")
async def rider_available_orders(current_user: User = Depends(require_rider)):
    return await db.orders.find(
        {"status": {"$in": ["confirmed", "preparing", "ready"]}, "rider_id": None},
        {"_id": 0},
    ).to_list(50)


@api_router.post("/rider/orders/{order_id}/accept")
async def rider_accept_order(
    order_id: str, current_user: User = Depends(require_rider)
):
    return {"message": "Order accepted"}


@api_router.patch("/rider/orders/{order_id}/status")
async def rider_update_status(
    order_id: str,
    request_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_rider),
):
    return {"message": "Status updated"}


@api_router.get("/rider/dashboard")
async def rider_dashboard(current_user: User = Depends(require_rider)):
    return {"today_deliveries": 0, "total_earnings": 0, "active_delivery": None}


@api_router.get("/rider/deliveries")
async def rider_deliveries(
    skip: int = 0, limit: int = 20, current_user: User = Depends(require_rider)
):
    return []