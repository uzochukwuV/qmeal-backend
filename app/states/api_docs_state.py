import reflex as rx
import httpx
import json
from typing import Any
import logging

endpoints_data = [
    {
        "method": "POST",
        "path": "/api/auth/register",
        "description": "Register new user",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": '{"email":"user@example.com","phone":"+1234567890","password":"password123","name":"John Doe"}',
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/login",
        "description": "Login with email/password",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": '{"email":"admin@qmeal.com","password":"password123"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/auth/me",
        "description": "Get current authenticated user",
        "category": "Auth",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/logout",
        "description": "Logout and clear session",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/push-token",
        "description": "Update push notification token",
        "category": "Auth",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"push_token":"ExponentPushToken[xxx]"}',
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/auth/profile",
        "description": "Update user profile",
        "category": "Auth",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"name":"New Name","email":"new@email.com"}',
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/register-owner",
        "description": "Register restaurant owner",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": '{"email":"owner@restaurant.com","password":"password123","name":"Owner Name","restaurant_name":"My Restaurant","cuisine_type":"Italian","description":"Great food","address":"123 Main St"}',
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/register-rider",
        "description": "Register rider",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": '{"email":"rider@qmeal.com","password":"password123","name":"Rider Name","phone":"+1234567890","vehicle_type":"motorcycle"}',
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/auth/register-admin",
        "description": "Register admin",
        "category": "Auth",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": '{"email":"admin@qmeal.com","password":"password123","name":"Admin Name","secret_key":"qmeal_admin_secret_2024"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/restaurants",
        "description": "List restaurants",
        "category": "Restaurants",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "cuisine, min_rating, price_level, search, sort_by",
    },
    {
        "method": "GET",
        "path": "/api/restaurants/{restaurant_id}",
        "description": "Get restaurant by ID",
        "category": "Restaurants",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/restaurants/{restaurant_id}/menu",
        "description": "Get restaurant menu",
        "category": "Restaurants",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/restaurants/{restaurant_id}/reviews",
        "description": "Get restaurant reviews",
        "category": "Restaurants",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/cuisines",
        "description": "Get list of cuisine types",
        "category": "Restaurants",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/favorites",
        "description": "Get user's favorites",
        "category": "Favorites",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/favorites/{restaurant_id}",
        "description": "Add to favorites",
        "category": "Favorites",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "DELETE",
        "path": "/api/favorites/{restaurant_id}",
        "description": "Remove from favorites",
        "category": "Favorites",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/favorites/check/{restaurant_id}",
        "description": "Check if favorite",
        "category": "Favorites",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/orders",
        "description": "Get user orders",
        "category": "Orders",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/orders",
        "description": "Create new order",
        "category": "Orders",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"restaurant_id":"rest_001","restaurant_name":"Bella Italia","items":[{"item_id":"item_001","name":"Margherita Pizza","price":14.99,"quantity":2,"restaurant_id":"rest_001"}],"subtotal":29.98,"delivery_fee":2.99,"total":32.97,"delivery_address":"456 Customer St"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/orders/{order_id}",
        "description": "Get order by ID",
        "category": "Orders",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/orders/{order_id}/status",
        "description": "Update order status",
        "category": "Orders",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"status":"preparing"}',
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/payments/create-intent",
        "description": "Create Stripe payment intent",
        "category": "Payments",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"amount":32.97,"currency":"usd"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/payments/config",
        "description": "Get Stripe config",
        "category": "Payments",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/reviews",
        "description": "Create review",
        "category": "Reviews",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": '{"restaurant_id":"rest_001","rating":5,"comment":"Excellent food!"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/notifications",
        "description": "Get user notifications",
        "category": "Notifications",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/notifications/{notification_id}/read",
        "description": "Mark notification as read",
        "category": "Notifications",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/notifications/read-all",
        "description": "Mark all as read",
        "category": "Notifications",
        "auth_required": True,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/dashboard",
        "description": "Owner dashboard stats",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/orders",
        "description": "Get restaurant orders",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "status",
    },
    {
        "method": "PATCH",
        "path": "/api/owner/orders/{order_id}/status",
        "description": "Update order status",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"status":"preparing"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/menu",
        "description": "Get menu items",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/owner/menu",
        "description": "Add menu item",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"name":"New Item","description":"Delicious","price":12.99,"category":"Main Dishes"}',
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/owner/menu/{item_id}",
        "description": "Update menu item",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"price":14.99,"is_available":true}',
        "query_params": "",
    },
    {
        "method": "DELETE",
        "path": "/api/owner/menu/{item_id}",
        "description": "Delete menu item",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/promotions",
        "description": "Get promotions",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/owner/promotions",
        "description": "Create promotion",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"code":"SAVE20","discount_percentage":20}',
        "query_params": "",
    },
    {
        "method": "DELETE",
        "path": "/api/owner/promotions/{promo_id}",
        "description": "Delete promotion",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/payouts",
        "description": "Get payout history",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/owner/payouts/request",
        "description": "Request payout",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"amount":100.00,"method":"bank_transfer"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/owner/restaurant",
        "description": "Get restaurant details",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/owner/restaurant",
        "description": "Update restaurant",
        "category": "Owner",
        "auth_required": True,
        "auth_role": "owner",
        "request_body_example": '{"name":"Updated Name","is_open":true}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/admin/dashboard",
        "description": "Platform dashboard stats",
        "category": "Admin",
        "auth_required": True,
        "auth_role": "admin",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/admin/restaurants",
        "description": "List all restaurants",
        "category": "Admin",
        "auth_required": True,
        "auth_role": "admin",
        "request_body_example": "",
        "query_params": "skip, limit",
    },
    {
        "method": "GET",
        "path": "/api/admin/users",
        "description": "List all users",
        "category": "Admin",
        "auth_required": True,
        "auth_role": "admin",
        "request_body_example": "",
        "query_params": "role, skip, limit",
    },
    {
        "method": "PATCH",
        "path": "/api/admin/users/{user_id}",
        "description": "Update user",
        "category": "Admin",
        "auth_required": True,
        "auth_role": "admin",
        "request_body_example": '{"role":"admin"}',
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/admin/restaurants/{restaurant_id}",
        "description": "Update restaurant",
        "category": "Admin",
        "auth_required": True,
        "auth_role": "admin",
        "request_body_example": '{"is_open":false}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/rider/available-orders",
        "description": "Get available orders",
        "category": "Rider",
        "auth_required": True,
        "auth_role": "rider",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "POST",
        "path": "/api/rider/orders/{order_id}/accept",
        "description": "Accept order",
        "category": "Rider",
        "auth_required": True,
        "auth_role": "rider",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "PATCH",
        "path": "/api/rider/orders/{order_id}/status",
        "description": "Update delivery status",
        "category": "Rider",
        "auth_required": True,
        "auth_role": "rider",
        "request_body_example": '{"status":"picked_up"}',
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/rider/dashboard",
        "description": "Rider dashboard stats",
        "category": "Rider",
        "auth_required": True,
        "auth_role": "rider",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/rider/deliveries",
        "description": "Delivery history",
        "category": "Rider",
        "auth_required": True,
        "auth_role": "rider",
        "request_body_example": "",
        "query_params": "skip, limit",
    },
    {
        "method": "POST",
        "path": "/api/seed",
        "description": "Seed database with sample data",
        "category": "Utility",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
    {
        "method": "GET",
        "path": "/api/health",
        "description": "Health check",
        "category": "Utility",
        "auth_required": False,
        "auth_role": "",
        "request_body_example": "",
        "query_params": "",
    },
]


class ApiDocsState(rx.State):
    selected_category: str = "Auth"
    selected_endpoint: dict[str, str | int | float | bool] = {}
    request_body: str = ""
    response_data: str = ""
    response_status: int = 0
    is_testing: bool = False
    auth_token: str = ""

    @rx.var
    def filtered_endpoints(self) -> list[dict[str, str | int | float | bool]]:
        return [ep for ep in endpoints_data if ep["category"] == self.selected_category]

    @rx.event
    def set_category(self, category: str):
        self.selected_category = category
        self.selected_endpoint = {}

    @rx.event
    def select_endpoint(self, endpoint: dict[str, str | int | float | bool]):
        if self.selected_endpoint.get("path") == endpoint.get(
            "path"
        ) and self.selected_endpoint.get("method") == endpoint.get("method"):
            self.selected_endpoint = {}
        else:
            self.selected_endpoint = endpoint
            self.request_body = str(endpoint.get("request_body_example", ""))
            self.response_data = ""
            self.response_status = 0

    @rx.event
    def set_request_body(self, body: str):
        self.request_body = body

    @rx.event
    def set_auth_token(self, token: str):
        self.auth_token = token

    @rx.event
    async def test_endpoint(self, method: str, path: str, body: str):
        self.is_testing = True
        yield
        try:
            host = self.router.page.host
            protocol = "https" if "localhost" not in host else "http"
            url = f"{protocol}://{host}{path}"
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            async with httpx.AsyncClient() as client:
                req_body = json.loads(body) if body else None
                if method == "GET":
                    res = await client.get(url, headers=headers)
                elif method == "POST":
                    res = await client.post(url, json=req_body, headers=headers)
                elif method == "PATCH":
                    res = await client.patch(url, json=req_body, headers=headers)
                elif method == "DELETE":
                    res = await client.delete(url, headers=headers)
                else:
                    self.is_testing = False
                    return
                self.response_status = res.status_code
                try:
                    self.response_data = json.dumps(res.json(), indent=2)
                except:
                    logging.exception("Unexpected error")
                    self.response_data = res.text
        except Exception as e:
            logging.exception("API request failed")
            self.response_status = 500
            self.response_data = str(e)
        finally:
            self.is_testing = False