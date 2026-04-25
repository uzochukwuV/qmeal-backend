import reflex as rx
from typing import Any
import logging
from app.utils.db import get_db

logger = logging.getLogger(__name__)


class OrdersState(rx.State):
    orders: list[dict[str, str | int | float | bool | list | dict]] = []
    selected_order: dict[str, str | int | float | bool | list | dict] = {}
    status_filter: str = "all"
    is_loading: bool = False
    show_order_detail: bool = False
    order_stats: dict[str, int] = {}

    @rx.event
    async def load_orders(self):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            query = {}
            if self.status_filter != "all":
                query["status"] = self.status_filter
            cursor = db.orders.find(query, {"_id": 0}).sort("created_at", -1)
            raw_orders = await cursor.to_list(length=100)
            for order in raw_orders:
                user = await db.users.find_one(
                    {"user_id": order.get("user_id")}, {"name": 1, "_id": 0}
                )
                order["customer_name"] = (
                    user.get("name", "Unknown") if user else "Unknown"
                )
            self.orders = raw_orders
            stats_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
            stats_result = await db.orders.aggregate(stats_pipeline).to_list(None)
            stats = {"all": 0}
            for stat in stats_result:
                stats[stat["_id"]] = stat["count"]
                stats["all"] += stat["count"]
            self.order_stats = stats
        except Exception as e:
            logger.exception(f"Error loading orders: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def load_order_detail(self, order_id: str):
        try:
            db = await get_db()
            order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
            if order:
                user = await db.users.find_one(
                    {"user_id": order.get("user_id")},
                    {"name": 1, "phone": 1, "email": 1, "_id": 0},
                )
                if user:
                    order["customer"] = user
                self.selected_order = order
                self.show_order_detail = True
        except Exception as e:
            logger.exception(f"Error loading order details: {e}")

    @rx.event
    async def update_order_status(self, order_id: str, new_status: str):
        try:
            db = await get_db()
            await db.orders.update_one(
                {"order_id": order_id}, {"$set": {"status": new_status}}
            )
            await self.load_orders()
            if self.selected_order.get("order_id") == order_id:
                self.selected_order["status"] = new_status
        except Exception as e:
            logger.exception(f"Error updating order status: {e}")

    @rx.event
    def set_status_filter(self, status: str):
        self.status_filter = status
        return OrdersState.load_orders

    @rx.event
    def toggle_order_detail(self):
        self.show_order_detail = not self.show_order_detail