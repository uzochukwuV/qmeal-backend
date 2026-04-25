from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Request, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import bcrypt
import jwt
import stripe

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
mongo_url = (
    os.environ["MONGO_URL"]
    or "mongodb+srv://vicezealor_db_user:bQHNL5fFkLKSgAxO@cluster0.ucm88sl.mongodb.net/?appName=Cluster0"
)
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get("DB_NAME", "qmeal_db")]
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
app = FastAPI(title="Qmeal API")
api_router = APIRouter(prefix="/api")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_jwt_token(user_id: str) -> str:
    """Create a JWT token for the user"""
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logging.exception("Unexpected error")
        return None
    except jwt.InvalidTokenError:
        logging.exception("Unexpected error")
        return None


async def get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from cookie or Authorization header"""
    token = request.cookies.get("auth_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


async def get_current_user(request: Request) -> Optional[User]:
    """Get current authenticated user"""
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
    """Dependency that requires authentication"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_rider(request: Request) -> User:
    """Dependency that requires rider role"""
    user = await require_auth(request)
    if user.role != "rider":
        raise HTTPException(status_code=403, detail="Rider access required")
    return user


async def require_admin(request: Request) -> User:
    """Dependency that requires admin role"""
    user = await require_auth(request)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def send_push_notification(
    user_id: str, title: str, body: str, data: dict = None
):
    """Send push notification to user via Expo"""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user or not user.get("push_token"):
        logger.info(f"No push token for user {user_id}")
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
            logger.info(f"Push notification sent: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logging.exception("Unexpected error")
        logger.error(f"Failed to send push notification: {e}")
        return False


@api_router.post("/auth/register", response_model=AuthResponse)
async def register(request_data: RegisterRequest, response: Response):
    """Register a new user with email/phone and password"""
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
        max_age=JWT_EXPIRATION_HOURS * 60 * 60,
    )
    return AuthResponse(
        user_id=user_id,
        email=request_data.email,
        phone=request_data.phone,
        name=request_data.name,
        picture=None,
        role="customer",
        restaurant_id=None,
        token=token,
    )


@api_router.post("/auth/login", response_model=AuthResponse)
async def login(request_data: LoginRequest, response: Response):
    """Login with email/phone and password"""
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
        max_age=JWT_EXPIRATION_HOURS * 60 * 60,
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
    """Get current authenticated user"""
    return current_user


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout and clear session"""
    response.delete_cookie(key="auth_token", path="/")
    return {"message": "Logged out successfully"}


@api_router.post("/auth/push-token")
async def update_push_token(
    request_data: UpdatePushTokenRequest, current_user: User = Depends(require_auth)
):
    """Update user's push notification token"""
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"push_token": request_data.push_token}},
    )
    return {"message": "Push token updated"}


@api_router.patch("/auth/profile")
async def update_profile(
    request_data: UpdateProfileRequest, current_user: User = Depends(require_auth)
):
    """Update user profile"""
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


@api_router.get("/restaurants", response_model=list[Restaurant])
async def get_restaurants(
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    price_level: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(
        default="rating", regex="^(rating|delivery_time|price)$"
    ),
):
    """Get all restaurants with optional filters"""
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
        sort_field = "delivery_time_min"
        sort_order = 1
    elif sort_by == "price":
        sort_field = "price_level"
        sort_order = 1
    restaurants = (
        await db.restaurants.find(query, {"_id": 0})
        .sort(sort_field, sort_order)
        .to_list(100)
    )
    return [Restaurant(**r) for r in restaurants]


@api_router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    """Get single restaurant by ID"""
    restaurant = await db.restaurants.find_one(
        {"restaurant_id": restaurant_id}, {"_id": 0}
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return Restaurant(**restaurant)


@api_router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
async def get_restaurant_menu(restaurant_id: str):
    """Get menu items for a restaurant"""
    items = await db.menu_items.find(
        {"restaurant_id": restaurant_id, "is_available": True}, {"_id": 0}
    ).to_list(100)
    return [MenuItem(**item) for item in items]


@api_router.get("/restaurants/{restaurant_id}/reviews", response_model=list[Review])
async def get_restaurant_reviews(restaurant_id: str):
    """Get reviews for a restaurant"""
    reviews = (
        await db.reviews.find({"restaurant_id": restaurant_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(50)
    )
    return [Review(**r) for r in reviews]


@api_router.get("/cuisines")
async def get_cuisines():
    """Get list of unique cuisines"""
    cuisines = await db.restaurants.distinct("cuisine_type")
    return {"cuisines": cuisines}


@api_router.get("/favorites", response_model=list[Restaurant])
async def get_favorites(current_user: User = Depends(require_auth)):
    """Get user's favorite restaurants"""
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
    """Add restaurant to favorites"""
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
    """Remove restaurant from favorites"""
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
    """Check if restaurant is in favorites"""
    existing = await db.favorites.find_one(
        {"user_id": current_user.user_id, "restaurant_id": restaurant_id}
    )
    return {"is_favorite": existing is not None}


@api_router.get("/orders", response_model=list[Order])
async def get_user_orders(current_user: User = Depends(require_auth)):
    """Get orders for current user"""
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
    """Create a new order"""
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
    await send_push_notification(
        current_user.user_id,
        "Order Confirmed!",
        f"Your order from {order_data.restaurant_name} has been confirmed.",
        {"order_id": order.order_id, "type": "order_confirmed"},
    )
    return order


@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user: User = Depends(require_auth)):
    """Get single order by ID"""
    order = await db.orders.find_one(
        {"order_id": order_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("rider_id"):
        rider = await db.users.find_one(
            {"user_id": order["rider_id"]},
            {"_id": 0, "name": 1, "phone": 1, "vehicle_type": 1},
        )
        if rider:
            order["rider"] = rider
    return order


@api_router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_auth),
):
    """Update order status (for demo/testing)"""
    valid_statuses = ["pending", "confirmed", "preparing", "on_the_way", "delivered"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"status": status_data.status}}
    )
    status_messages = {
        "preparing": "Your order is being prepared!",
        "on_the_way": "Your order is on the way!",
        "delivered": "Your order has been delivered!",
    }
    if status_data.status in status_messages:
        await send_push_notification(
            order["user_id"],
            f"Order Update - {status_data.status.replace('_', ' ').title()}",
            status_messages[status_data.status],
            {
                "order_id": order_id,
                "type": "order_status",
                "status": status_data.status,
            },
        )
    return {"message": "Status updated", "status": status_data.status}


@api_router.post("/payments/create-intent")
async def create_payment_intent(
    request_data: CreatePaymentIntentRequest, current_user: User = Depends(require_auth)
):
    """Create a Stripe payment intent"""
    try:
        amount_cents = int(request_data.amount * 100)
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=request_data.currency,
                metadata={"user_id": current_user.user_id},
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "publishable_key": STRIPE_PUBLISHABLE_KEY,
            }
        except stripe.error.AuthenticationError:
            logging.exception("Unexpected error")
            mock_intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
            return {
                "client_secret": f"{mock_intent_id}_secret_mock",
                "payment_intent_id": mock_intent_id,
                "publishable_key": STRIPE_PUBLISHABLE_KEY,
                "mock": True,
                "message": "Using mock payment intent - replace with real Stripe keys for production",
            }
    except Exception as e:
        logging.exception("Unexpected error")
        logger.error(f"Payment intent error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment intent")


@api_router.get("/payments/config")
async def get_payment_config():
    """Get Stripe publishable key for frontend"""
    return {
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
        "is_mock": "mock" in STRIPE_PUBLISHABLE_KEY,
    }


@api_router.post("/reviews", response_model=Review)
async def create_review(
    review_data: CreateReviewRequest, current_user: User = Depends(require_auth)
):
    """Create a new review"""
    restaurant = await db.restaurants.find_one(
        {"restaurant_id": review_data.restaurant_id}, {"_id": 0}
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    review = Review(
        restaurant_id=review_data.restaurant_id,
        user_id=current_user.user_id,
        user_name=current_user.name,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    await db.reviews.insert_one(review.dict())
    all_reviews = await db.reviews.find(
        {"restaurant_id": review_data.restaurant_id}, {"_id": 0}
    ).to_list(1000)
    if all_reviews:
        avg_rating = sum((r["rating"] for r in all_reviews)) / len(all_reviews)
        await db.restaurants.update_one(
            {"restaurant_id": review_data.restaurant_id},
            {
                "$set": {
                    "rating": round(avg_rating, 1),
                    "review_count": len(all_reviews),
                }
            },
        )
    return review


@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(require_auth)):
    """Get user's notifications"""
    notifications = (
        await db.notifications.find({"user_id": current_user.user_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(50)
    )
    return notifications


@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str, current_user: User = Depends(require_auth)
):
    """Mark notification as read"""
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user.user_id},
        {"$set": {"read": True}},
    )
    return {"message": "Notification marked as read"}


@api_router.post("/notifications/read-all")
async def mark_all_notifications_read(current_user: User = Depends(require_auth)):
    """Mark all notifications as read"""
    await db.notifications.update_many(
        {"user_id": current_user.user_id}, {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}


async def require_owner(request: Request) -> User:
    """Dependency that requires owner authentication"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    if not user.restaurant_id:
        raise HTTPException(status_code=403, detail="No restaurant assigned")
    return user


@api_router.post("/auth/register-owner", response_model=AuthResponse)
async def register_owner(request_data: RegisterOwnerRequest, response: Response):
    """Register a new restaurant owner with their restaurant"""
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
    hashed_password = hash_password(request_data.password)
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "name": request_data.name,
        "password_hash": hashed_password,
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
    """Register a new rider"""
    existing = await db.users.find_one({"email": request_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = hash_password(request_data.password)
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "phone": request_data.phone,
        "name": request_data.name,
        "password_hash": hashed_password,
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
    """Register a new admin (requires secret key)"""
    if request_data.secret_key != "qmeal_admin_secret_2024":
        raise HTTPException(status_code=403, detail="Invalid admin secret key")
    existing = await db.users.find_one({"email": request_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = hash_password(request_data.password)
    user = {
        "user_id": user_id,
        "email": request_data.email,
        "name": request_data.name,
        "password_hash": hashed_password,
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


@api_router.get("/owner/dashboard")
async def owner_dashboard(current_user: User = Depends(require_owner)):
    """Get dashboard stats for restaurant owner"""
    restaurant_id = current_user.restaurant_id
    restaurant = await db.restaurants.find_one(
        {"restaurant_id": restaurant_id}, {"_id": 0}
    )
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_orders = await db.orders.count_documents(
        {"restaurant_id": restaurant_id, "created_at": {"$gte": today_start}}
    )
    pipeline = [
        {
            "$match": {
                "restaurant_id": restaurant_id,
                "created_at": {"$gte": today_start},
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$total"}}},
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    today_revenue = revenue_result[0]["total"] if revenue_result else 0
    pipeline_all = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}},
    ]
    all_revenue_result = await db.orders.aggregate(pipeline_all).to_list(1)
    total_revenue = all_revenue_result[0]["total"] if all_revenue_result else 0
    pending_orders = await db.orders.count_documents(
        {"restaurant_id": restaurant_id, "status": {"$in": ["pending", "confirmed"]}}
    )
    total_orders = await db.orders.count_documents({"restaurant_id": restaurant_id})
    menu_count = await db.menu_items.count_documents({"restaurant_id": restaurant_id})
    review_count = await db.reviews.count_documents({"restaurant_id": restaurant_id})
    return {
        "restaurant": restaurant,
        "stats": {
            "today_orders": today_orders,
            "today_revenue": round(today_revenue, 2),
            "total_revenue": round(total_revenue, 2),
            "pending_orders": pending_orders,
            "total_orders": total_orders,
            "menu_items": menu_count,
            "review_count": review_count,
            "rating": restaurant.get("rating", 0) if restaurant else 0,
        },
    }


@api_router.get("/owner/orders")
async def owner_get_orders(
    status: Optional[str] = None, current_user: User = Depends(require_owner)
):
    """Get all orders for the owner's restaurant"""
    query = {"restaurant_id": current_user.restaurant_id}
    if status:
        query["status"] = status
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    for order in orders:
        user = await db.users.find_one(
            {"user_id": order["user_id"]}, {"name": 1, "_id": 0}
        )
        order["customer_name"] = user.get("name", "Unknown") if user else "Unknown"
    return orders


@api_router.patch("/owner/orders/{order_id}/status")
async def owner_update_order_status(
    order_id: str,
    request_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_owner),
):
    """Update order status (owner only)"""
    valid_statuses = [
        "pending",
        "confirmed",
        "preparing",
        "ready",
        "picked_up",
        "delivered",
        "cancelled",
    ]
    if request_data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )
    order = await db.orders.find_one(
        {"order_id": order_id, "restaurant_id": current_user.restaurant_id}
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"status": request_data.status}}
    )
    status_messages = {
        "confirmed": "Your order has been confirmed!",
        "preparing": "Your food is being prepared",
        "ready": "Your order is ready for pickup!",
        "picked_up": "Your order is on its way!",
        "delivered": "Your order has been delivered!",
        "cancelled": "Your order has been cancelled",
    }
    if request_data.status in status_messages:
        await send_push_notification(
            order["user_id"],
            f"Order #{order_id[:8]}",
            status_messages[request_data.status],
            {
                "type": "order_status",
                "order_id": order_id,
                "status": request_data.status,
            },
        )
    return {"message": "Order status updated", "status": request_data.status}


@api_router.get("/owner/menu")
async def owner_get_menu(current_user: User = Depends(require_owner)):
    """Get all menu items for the owner's restaurant"""
    items = await db.menu_items.find(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    ).to_list(200)
    return items


@api_router.post("/owner/menu")
async def owner_add_menu_item(
    request_data: AddMenuItemRequest, current_user: User = Depends(require_owner)
):
    """Add a new menu item"""
    item = MenuItem(
        restaurant_id=current_user.restaurant_id,
        name=request_data.name,
        description=request_data.description,
        price=request_data.price,
        category=request_data.category,
        image_url=request_data.image_url,
        is_available=request_data.is_available,
        is_popular=request_data.is_popular,
    )
    await db.menu_items.insert_one(item.dict())
    return item.dict()


@api_router.patch("/owner/menu/{item_id}")
async def owner_update_menu_item(
    item_id: str,
    request_data: UpdateMenuItemRequest,
    current_user: User = Depends(require_owner),
):
    """Update an existing menu item"""
    existing = await db.menu_items.find_one(
        {"item_id": item_id, "restaurant_id": current_user.restaurant_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Menu item not found")
    update_fields = {k: v for k, v in request_data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.menu_items.update_one({"item_id": item_id}, {"$set": update_fields})
    updated = await db.menu_items.find_one({"item_id": item_id}, {"_id": 0})
    return updated


@api_router.delete("/owner/menu/{item_id}")
async def owner_delete_menu_item(
    item_id: str, current_user: User = Depends(require_owner)
):
    """Delete a menu item"""
    result = await db.menu_items.delete_one(
        {"item_id": item_id, "restaurant_id": current_user.restaurant_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted"}


@api_router.get("/owner/promotions")
async def owner_get_promotions(current_user: User = Depends(require_owner)):
    """Get list of promotions"""
    cursor = db.promotions.find(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    ).sort("created_at", -1)
    promotions = await cursor.to_list(length=50)
    return promotions


class CreatePromotionRequest(BaseModel):
    code: str
    discount_percentage: float


@api_router.post("/owner/promotions")
async def owner_create_promotion(
    request_data: CreatePromotionRequest, current_user: User = Depends(require_owner)
):
    """Create a new promotion"""
    if request_data.discount_percentage <= 0 or request_data.discount_percentage > 100:
        raise HTTPException(status_code=400, detail="Invalid discount percentage")
    promotion = {
        "promo_id": f"promo_{uuid.uuid4().hex[:12]}",
        "restaurant_id": current_user.restaurant_id,
        "code": request_data.code.upper(),
        "discount_percentage": request_data.discount_percentage,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    await db.promotions.insert_one(promotion)
    return {"message": "Promotion created successfully", "promotion": promotion}


@api_router.delete("/owner/promotions/{promo_id}")
async def owner_delete_promotion(
    promo_id: str, current_user: User = Depends(require_owner)
):
    """Delete a promotion"""
    result = await db.promotions.delete_one(
        {"promo_id": promo_id, "restaurant_id": current_user.restaurant_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"message": "Promotion deleted successfully"}


@api_router.get("/owner/payouts")
async def owner_get_payouts(current_user: User = Depends(require_owner)):
    """Get payout history and available balance"""
    pipeline = [
        {
            "$match": {
                "restaurant_id": current_user.restaurant_id,
                "status": "delivered",
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$total"}}},
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    payout_pipeline = [
        {"$match": {"user_id": current_user.user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    payout_result = await db.payouts.aggregate(payout_pipeline).to_list(1)
    total_payouts = payout_result[0]["total"] if payout_result else 0
    available_balance = max(0, total_revenue - total_payouts)
    cursor = db.payouts.find({"user_id": current_user.user_id}, {"_id": 0}).sort(
        "created_at", -1
    )
    payout_history = await cursor.to_list(length=20)
    return {"available_balance": available_balance, "history": payout_history}


class PayoutRequest(BaseModel):
    amount: float
    method: str = "bank_transfer"


@api_router.post("/owner/payouts/request")
async def owner_request_payout(
    request_data: PayoutRequest, current_user: User = Depends(require_owner)
):
    """Request a payout"""
    if request_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    payout = {
        "payout_id": f"pay_{uuid.uuid4().hex[:12]}",
        "user_id": current_user.user_id,
        "amount": request_data.amount,
        "status": "pending",
        "method": request_data.method,
        "created_at": datetime.now(timezone.utc),
    }
    await db.payouts.insert_one(payout)
    return {"message": "Payout requested successfully"}


@api_router.get("/owner/restaurant")
async def owner_get_restaurant(current_user: User = Depends(require_owner)):
    """Get the owner's restaurant details"""
    restaurant = await db.restaurants.find_one(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@api_router.patch("/owner/restaurant")
async def owner_update_restaurant(
    request_data: UpdateRestaurantRequest, current_user: User = Depends(require_owner)
):
    """Update restaurant details"""
    update_fields = {k: v for k, v in request_data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.restaurants.update_one(
        {"restaurant_id": current_user.restaurant_id}, {"$set": update_fields}
    )
    updated = await db.restaurants.find_one(
        {"restaurant_id": current_user.restaurant_id}, {"_id": 0}
    )
    return updated


@api_router.post("/seed")
async def seed_database():
    """Seed the database with sample data"""
    existing = await db.restaurants.count_documents({})
    if existing > 0:
        return {"message": "Database already seeded", "restaurant_count": existing}
    restaurants = [
        {
            "restaurant_id": "rest_001",
            "name": "Bella Italia",
            "description": "Authentic Italian cuisine with handmade pasta and wood-fired pizzas",
            "cuisine_type": "Italian",
            "rating": 4.7,
            "review_count": 234,
            "price_level": 2,
            "image_url": "https://images.unsplash.com/photo-1615719413546-198b25453f85",
            "address": "123 Main Street, Downtown",
            "latitude": 40.7128,
            "longitude": -74.006,
            "delivery_time_min": 25,
            "delivery_time_max": 40,
            "delivery_fee": 2.99,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_002",
            "name": "Tokyo Ramen House",
            "description": "Traditional Japanese ramen and authentic Asian dishes",
            "cuisine_type": "Japanese",
            "rating": 4.8,
            "review_count": 189,
            "price_level": 2,
            "image_url": "https://images.unsplash.com/photo-1676300185004-c31cf62d3bc8",
            "address": "456 Oak Avenue, Midtown",
            "latitude": 40.758,
            "longitude": -73.9855,
            "delivery_time_min": 20,
            "delivery_time_max": 35,
            "delivery_fee": 1.99,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_003",
            "name": "Burger Republic",
            "description": "Gourmet burgers made with premium Angus beef and fresh ingredients",
            "cuisine_type": "American",
            "rating": 4.5,
            "review_count": 456,
            "price_level": 1,
            "image_url": "https://images.unsplash.com/photo-1651440204227-a9a5b9d19712",
            "address": "789 Elm Street, Uptown",
            "latitude": 40.7829,
            "longitude": -73.9654,
            "delivery_time_min": 15,
            "delivery_time_max": 30,
            "delivery_fee": 0.99,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_004",
            "name": "Spice Garden",
            "description": "Aromatic Indian curries and tandoori specialties",
            "cuisine_type": "Indian",
            "rating": 4.6,
            "review_count": 178,
            "price_level": 2,
            "image_url": "https://images.unsplash.com/photo-1694184191737-778bc1b5c4e8",
            "address": "321 Spice Lane, East Side",
            "latitude": 40.7489,
            "longitude": -73.968,
            "delivery_time_min": 30,
            "delivery_time_max": 45,
            "delivery_fee": 2.49,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_005",
            "name": "Le Petit Bistro",
            "description": "French cuisine with a modern twist in an elegant setting",
            "cuisine_type": "French",
            "rating": 4.9,
            "review_count": 98,
            "price_level": 4,
            "image_url": "https://images.unsplash.com/photo-1683538503204-fec7fc504067",
            "address": "555 Boulevard Ave, West End",
            "latitude": 40.7614,
            "longitude": -73.9776,
            "delivery_time_min": 35,
            "delivery_time_max": 50,
            "delivery_fee": 4.99,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_006",
            "name": "Taco Fiesta",
            "description": "Authentic Mexican street food and margaritas",
            "cuisine_type": "Mexican",
            "rating": 4.4,
            "review_count": 312,
            "price_level": 1,
            "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47",
            "address": "777 Fiesta Way, South Side",
            "latitude": 40.7282,
            "longitude": -73.7949,
            "delivery_time_min": 20,
            "delivery_time_max": 35,
            "delivery_fee": 1.49,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_007",
            "name": "Dragon Palace",
            "description": "Traditional Chinese cuisine with dim sum and Cantonese favorites",
            "cuisine_type": "Chinese",
            "rating": 4.3,
            "review_count": 267,
            "price_level": 2,
            "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d",
            "address": "888 Dragon Street, Chinatown",
            "latitude": 40.7157,
            "longitude": -73.997,
            "delivery_time_min": 25,
            "delivery_time_max": 40,
            "delivery_fee": 2.29,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "restaurant_id": "rest_008",
            "name": "Mediterranean Grill",
            "description": "Fresh Mediterranean flavors with grilled meats and seafood",
            "cuisine_type": "Mediterranean",
            "rating": 4.6,
            "review_count": 145,
            "price_level": 3,
            "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947",
            "address": "999 Olive Road, Harbor District",
            "latitude": 40.7023,
            "longitude": -74.0156,
            "delivery_time_min": 30,
            "delivery_time_max": 45,
            "delivery_fee": 3.49,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        },
    ]
    await db.restaurants.insert_many(restaurants)
    menu_items = [
        {
            "item_id": "item_001",
            "restaurant_id": "rest_001",
            "name": "Margherita Pizza",
            "description": "Fresh mozzarella, tomato sauce, and basil",
            "price": 14.99,
            "category": "Pizza",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_002",
            "restaurant_id": "rest_001",
            "name": "Spaghetti Carbonara",
            "description": "Creamy pasta with bacon and parmesan",
            "price": 16.99,
            "category": "Pasta",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_003",
            "restaurant_id": "rest_001",
            "name": "Tiramisu",
            "description": "Classic Italian dessert with coffee and mascarpone",
            "price": 8.99,
            "category": "Desserts",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_004",
            "restaurant_id": "rest_001",
            "name": "Bruschetta",
            "description": "Toasted bread with tomatoes, garlic, and olive oil",
            "price": 9.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_005",
            "restaurant_id": "rest_001",
            "name": "Lasagna",
            "description": "Layers of pasta, meat sauce, and cheese",
            "price": 18.99,
            "category": "Pasta",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_006",
            "restaurant_id": "rest_002",
            "name": "Tonkotsu Ramen",
            "description": "Rich pork bone broth with chashu and soft egg",
            "price": 15.99,
            "category": "Ramen",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_007",
            "restaurant_id": "rest_002",
            "name": "Gyoza (6 pcs)",
            "description": "Pan-fried pork dumplings",
            "price": 8.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_008",
            "restaurant_id": "rest_002",
            "name": "Chicken Katsu Curry",
            "description": "Crispy chicken cutlet with Japanese curry",
            "price": 16.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_009",
            "restaurant_id": "rest_002",
            "name": "Miso Soup",
            "description": "Traditional Japanese soup with tofu and seaweed",
            "price": 4.99,
            "category": "Soups",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_010",
            "restaurant_id": "rest_002",
            "name": "Spicy Miso Ramen",
            "description": "Spicy miso broth with ground pork and corn",
            "price": 16.99,
            "category": "Ramen",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_011",
            "restaurant_id": "rest_003",
            "name": "Classic Smash Burger",
            "description": "Double patty with cheese, lettuce, tomato",
            "price": 12.99,
            "category": "Burgers",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_012",
            "restaurant_id": "rest_003",
            "name": "Bacon BBQ Burger",
            "description": "Angus beef with bacon, cheddar, and BBQ sauce",
            "price": 14.99,
            "category": "Burgers",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_013",
            "restaurant_id": "rest_003",
            "name": "Loaded Fries",
            "description": "Crispy fries with cheese, bacon, and sour cream",
            "price": 8.99,
            "category": "Sides",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_014",
            "restaurant_id": "rest_003",
            "name": "Onion Rings",
            "description": "Beer-battered onion rings",
            "price": 6.99,
            "category": "Sides",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_015",
            "restaurant_id": "rest_003",
            "name": "Milkshake",
            "description": "Choose vanilla, chocolate, or strawberry",
            "price": 5.99,
            "category": "Drinks",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_016",
            "restaurant_id": "rest_004",
            "name": "Butter Chicken",
            "description": "Tender chicken in creamy tomato sauce",
            "price": 16.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_017",
            "restaurant_id": "rest_004",
            "name": "Lamb Biryani",
            "description": "Fragrant basmati rice with spiced lamb",
            "price": 18.99,
            "category": "Rice Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_018",
            "restaurant_id": "rest_004",
            "name": "Garlic Naan",
            "description": "Fresh baked bread with garlic butter",
            "price": 3.99,
            "category": "Bread",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_019",
            "restaurant_id": "rest_004",
            "name": "Samosa (2 pcs)",
            "description": "Crispy pastry filled with spiced potatoes",
            "price": 5.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_020",
            "restaurant_id": "rest_004",
            "name": "Palak Paneer",
            "description": "Cottage cheese in spinach gravy",
            "price": 14.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_021",
            "restaurant_id": "rest_005",
            "name": "Duck Confit",
            "description": "Slow-cooked duck leg with roasted potatoes",
            "price": 32.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_022",
            "restaurant_id": "rest_005",
            "name": "French Onion Soup",
            "description": "Classic soup with melted gruyere cheese",
            "price": 12.99,
            "category": "Soups",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_023",
            "restaurant_id": "rest_005",
            "name": "Steak Frites",
            "description": "Grilled ribeye with herb butter and fries",
            "price": 38.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_024",
            "restaurant_id": "rest_005",
            "name": "Crème Brûlée",
            "description": "Classic vanilla custard with caramelized sugar",
            "price": 10.99,
            "category": "Desserts",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_025",
            "restaurant_id": "rest_005",
            "name": "Escargot",
            "description": "Garlic butter snails in shell",
            "price": 16.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_026",
            "restaurant_id": "rest_006",
            "name": "Street Tacos (3)",
            "description": "Choice of carnitas, chicken, or steak",
            "price": 10.99,
            "category": "Tacos",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_027",
            "restaurant_id": "rest_006",
            "name": "Burrito Bowl",
            "description": "Rice, beans, protein, and toppings",
            "price": 12.99,
            "category": "Bowls",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_028",
            "restaurant_id": "rest_006",
            "name": "Guacamole & Chips",
            "description": "Fresh made guacamole with tortilla chips",
            "price": 8.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_029",
            "restaurant_id": "rest_006",
            "name": "Quesadilla",
            "description": "Grilled tortilla with cheese and protein",
            "price": 11.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_030",
            "restaurant_id": "rest_006",
            "name": "Churros",
            "description": "Fried dough with cinnamon sugar and chocolate",
            "price": 6.99,
            "category": "Desserts",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_031",
            "restaurant_id": "rest_007",
            "name": "Kung Pao Chicken",
            "description": "Spicy chicken with peanuts and peppers",
            "price": 15.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_032",
            "restaurant_id": "rest_007",
            "name": "Dim Sum Platter",
            "description": "Assorted dumplings and buns",
            "price": 18.99,
            "category": "Dim Sum",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_033",
            "restaurant_id": "rest_007",
            "name": "Peking Duck",
            "description": "Crispy duck with pancakes and hoisin",
            "price": 38.99,
            "category": "Specialties",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_034",
            "restaurant_id": "rest_007",
            "name": "Fried Rice",
            "description": "Wok-fried rice with egg and vegetables",
            "price": 10.99,
            "category": "Rice Dishes",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_035",
            "restaurant_id": "rest_007",
            "name": "Spring Rolls (4)",
            "description": "Crispy vegetable spring rolls",
            "price": 7.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_036",
            "restaurant_id": "rest_008",
            "name": "Grilled Lamb Chops",
            "description": "Marinated lamb with Mediterranean herbs",
            "price": 28.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_037",
            "restaurant_id": "rest_008",
            "name": "Mixed Grill Platter",
            "description": "Chicken, lamb, and beef kebabs",
            "price": 24.99,
            "category": "Main Dishes",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_038",
            "restaurant_id": "rest_008",
            "name": "Hummus & Pita",
            "description": "Creamy hummus with warm pita bread",
            "price": 8.99,
            "category": "Appetizers",
            "is_available": True,
            "is_popular": True,
        },
        {
            "item_id": "item_039",
            "restaurant_id": "rest_008",
            "name": "Greek Salad",
            "description": "Fresh vegetables with feta and olives",
            "price": 11.99,
            "category": "Salads",
            "is_available": True,
            "is_popular": False,
        },
        {
            "item_id": "item_040",
            "restaurant_id": "rest_008",
            "name": "Baklava",
            "description": "Honey-soaked phyllo pastry with nuts",
            "price": 7.99,
            "category": "Desserts",
            "is_available": True,
            "is_popular": False,
        },
    ]
    await db.menu_items.insert_many(menu_items)
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("phone", unique=True, sparse=True)
    await db.users.create_index("user_id", unique=True)
    await db.restaurants.create_index("restaurant_id", unique=True)
    await db.menu_items.create_index("restaurant_id")
    await db.orders.create_index("user_id")
    await db.favorites.create_index([("user_id", 1), ("restaurant_id", 1)], unique=True)
    await db.notifications.create_index("user_id")
    return {
        "message": "Database seeded successfully",
        "restaurants": len(restaurants),
        "menu_items": len(menu_items),
    }


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@api_router.get("/admin/dashboard")
async def admin_dashboard(current_user: User = Depends(require_admin)):
    """Get global platform stats for admin"""
    total_users = await db.users.count_documents({})
    total_restaurants = await db.restaurants.count_documents({})
    total_orders = await db.orders.count_documents({})
    pipeline_all = [{"$group": {"_id": None, "total": {"$sum": "$total"}}}]
    all_revenue_result = await db.orders.aggregate(pipeline_all).to_list(1)
    total_revenue = all_revenue_result[0]["total"] if all_revenue_result else 0
    return {
        "total_users": total_users,
        "total_restaurants": total_restaurants,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
    }


@api_router.get("/admin/restaurants")
async def admin_list_restaurants(
    skip: int = 0, limit: int = 20, current_user: User = Depends(require_admin)
):
    """List all restaurants for admin"""
    cursor = (
        db.restaurants.find({}, {"_id": 0})
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )
    restaurants = await cursor.to_list(length=limit)
    return restaurants


@api_router.get("/admin/users")
async def admin_list_users(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
):
    """List all users for admin"""
    query = {}
    if role:
        query["role"] = role
    cursor = (
        db.users.find(query, {"_id": 0, "password_hash": 0})
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )
    users = await cursor.to_list(length=limit)
    return users


class AdminUpdateUserRequest(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None


@api_router.patch("/admin/users/{user_id}")
async def admin_update_user(
    user_id: str,
    request_data: AdminUpdateUserRequest,
    current_user: User = Depends(require_admin),
):
    """Update user by admin"""
    update_fields = request_data.dict(exclude_unset=True)
    if not update_fields:
        return {"message": "No fields to update"}
    result = await db.users.update_one({"user_id": user_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}


class AdminUpdateRestaurantRequest(BaseModel):
    is_open: Optional[bool] = None
    delivery_fee: Optional[float] = None


@api_router.patch("/admin/restaurants/{restaurant_id}")
async def admin_update_restaurant(
    restaurant_id: str,
    request_data: AdminUpdateRestaurantRequest,
    current_user: User = Depends(require_admin),
):
    """Update restaurant by admin"""
    update_fields = request_data.dict(exclude_unset=True)
    if not update_fields:
        return {"message": "No fields to update"}
    result = await db.restaurants.update_one(
        {"restaurant_id": restaurant_id}, {"$set": update_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"message": "Restaurant updated successfully"}


@api_router.get("/rider/available-orders")
async def rider_available_orders(current_user: User = Depends(require_rider)):
    """Get list of orders waiting for a rider"""
    cursor = db.orders.find(
        {"status": {"$in": ["confirmed", "preparing", "ready"]}, "rider_id": None},
        {"_id": 0},
    ).sort("created_at", -1)
    orders = await cursor.to_list(length=50)
    return orders


@api_router.post("/rider/orders/{order_id}/accept")
async def rider_accept_order(
    order_id: str, current_user: User = Depends(require_rider)
):
    """Accept an order for delivery"""
    order = await db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("rider_id"):
        raise HTTPException(status_code=400, detail="Order already assigned to a rider")
    delivery_id = f"del_{uuid.uuid4().hex[:12]}"
    delivery = {
        "delivery_id": delivery_id,
        "order_id": order_id,
        "rider_id": current_user.user_id,
        "restaurant_id": order["restaurant_id"],
        "status": "accepted",
        "pickup_location": {"address": order.get("restaurant_name", "Restaurant")},
        "dropoff_location": {"address": order.get("delivery_address", "Customer")},
        "delivery_fee": order.get("delivery_fee", 2.99),
        "tip": 0.0,
        "created_at": datetime.now(timezone.utc),
        "accepted_at": datetime.now(timezone.utc),
    }
    await db.deliveries.insert_one(delivery)
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"rider_id": current_user.user_id}}
    )
    await send_push_notification(
        order["user_id"],
        "Rider Assigned",
        f"{current_user.name} is heading to the restaurant.",
        {"order_id": order_id, "type": "rider_assigned"},
    )
    return {"message": "Order accepted", "delivery_id": delivery_id}


@api_router.patch("/rider/orders/{order_id}/status")
async def rider_update_status(
    order_id: str,
    status_data: UpdateOrderStatusRequest,
    current_user: User = Depends(require_rider),
):
    """Update delivery status (picked_up, on_the_way, delivered)"""
    valid_statuses = ["picked_up", "on_the_way", "delivered"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid rider status")
    order = await db.orders.find_one(
        {"order_id": order_id, "rider_id": current_user.user_id}
    )
    if not order:
        raise HTTPException(
            status_code=404, detail="Order not found or not assigned to you"
        )
    await db.orders.update_one(
        {"order_id": order_id}, {"$set": {"status": status_data.status}}
    )
    delivery_update = {"status": status_data.status}
    if status_data.status == "picked_up":
        delivery_update["picked_up_at"] = datetime.now(timezone.utc)
    elif status_data.status == "delivered":
        delivery_update["delivered_at"] = datetime.now(timezone.utc)
    await db.deliveries.update_one({"order_id": order_id}, {"$set": delivery_update})
    status_messages = {
        "picked_up": "Your order has been picked up!",
        "on_the_way": "Your order is on the way!",
        "delivered": "Your order has been delivered!",
    }
    await send_push_notification(
        order["user_id"],
        "Order Update",
        status_messages[status_data.status],
        {"order_id": order_id, "type": f"order_{status_data.status}"},
    )
    return {"message": f"Status updated to {status_data.status}"}


@api_router.get("/rider/dashboard")
async def rider_dashboard(current_user: User = Depends(require_rider)):
    """Get rider stats"""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_deliveries = await db.deliveries.count_documents(
        {
            "rider_id": current_user.user_id,
            "created_at": {"$gte": today_start},
            "status": "delivered",
        }
    )
    pipeline = [
        {"$match": {"rider_id": current_user.user_id, "status": "delivered"}},
        {"$group": {"_id": None, "total": {"$sum": "$delivery_fee"}}},
    ]
    revenue_result = await db.deliveries.aggregate(pipeline).to_list(1)
    total_earnings = revenue_result[0]["total"] if revenue_result else 0
    active_delivery = await db.deliveries.find_one(
        {
            "rider_id": current_user.user_id,
            "status": {"$in": ["accepted", "picked_up", "on_the_way"]},
        },
        {"_id": 0},
    )
    if active_delivery:
        order = await db.orders.find_one(
            {"order_id": active_delivery["order_id"]}, {"_id": 0}
        )
        active_delivery["order"] = order
    return {
        "today_deliveries": today_deliveries,
        "total_earnings": total_earnings,
        "active_delivery": active_delivery,
    }


@api_router.get("/rider/deliveries")
async def rider_deliveries(
    skip: int = 0, limit: int = 20, current_user: User = Depends(require_rider)
):
    """Get rider delivery history"""
    cursor = (
        db.deliveries.find({"rider_id": current_user.user_id}, {"_id": 0})
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )
    deliveries = await cursor.to_list(length=limit)
    for delivery in deliveries:
        order = await db.orders.find_one({"order_id": delivery["order_id"]}, {"_id": 0})
        delivery["order"] = order
    return deliveries


app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()