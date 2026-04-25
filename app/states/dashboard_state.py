import reflex as rx
from typing import Any
import logging
from app.utils.db import get_db

logger = logging.getLogger(__name__)


class DashboardState(rx.State):
    total_users: int = 0
    total_restaurants: int = 0
    total_orders: int = 0
    total_revenue: float = 0.0
    recent_orders: list[dict[str, str | float | int]] = []
    top_restaurants: list[dict[str, str | float | int]] = []

    @rx.event
    async def load_dashboard(self):
        try:
            db = await get_db()
            self.total_users = await db.users.count_documents({})
            self.total_restaurants = await db.restaurants.count_documents({})
            self.total_orders = await db.orders.count_documents({})
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total"}}}]
            revenue_result = await db.orders.aggregate(pipeline).to_list(1)
            self.total_revenue = (
                float(revenue_result[0]["total"]) if revenue_result else 0.0
            )
            orders_cursor = (
                db.orders.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
            )
            orders_list = await orders_cursor.to_list(length=5)
            formatted_orders = []
            for order in orders_list:
                user = await db.users.find_one(
                    {"user_id": order.get("user_id")}, {"name": 1, "_id": 0}
                )
                customer_name = user.get("name", "Unknown") if user else "Unknown"
                dt = order.get("created_at")
                date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else ""
                formatted_orders.append(
                    {
                        "order_id": str(order.get("order_id", ""))[:8],
                        "restaurant_name": str(order.get("restaurant_name", "")),
                        "customer": customer_name,
                        "status": str(order.get("status", "")),
                        "total": float(order.get("total", 0.0)),
                        "date": date_str,
                    }
                )
            self.recent_orders = formatted_orders
            rests_cursor = (
                db.restaurants.find({}, {"_id": 0}).sort("rating", -1).limit(5)
            )
            rests_list = await rests_cursor.to_list(length=5)
            formatted_rests = []
            for rest in rests_list:
                formatted_rests.append(
                    {
                        "name": str(rest.get("name", "")),
                        "rating": float(rest.get("rating", 0.0)),
                        "review_count": int(rest.get("review_count", 0)),
                        "cuisine_type": str(rest.get("cuisine_type", "")),
                    }
                )
            self.top_restaurants = formatted_rests
        except Exception as e:
            logger.exception(f"Error loading dashboard stats: {e}")