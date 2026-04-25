import reflex as rx
import logging
from app.utils.db import get_db
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RidersState(rx.State):
    riders: list[dict[str, str | int | float | bool | list | dict]] = []
    active_deliveries: list[dict[str, str | int | float | bool | list | dict]] = []
    delivery_history: list[dict[str, str | int | float | bool | list | dict]] = []
    is_loading: bool = False
    selected_rider: dict[str, str | int | float | bool | list | dict] = {}
    show_rider_detail: bool = False
    total_riders: int = 0
    total_deliveries_today: int = 0
    total_earnings: float = 0.0

    @rx.event
    async def load_riders(self):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            await self.load_active_deliveries_logic(db)
            cursor = db.users.find({"role": "rider"}, {"password_hash": 0, "_id": 0})
            raw_riders = await cursor.to_list(length=100)
            self.total_riders = len(raw_riders)
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            self.total_deliveries_today = await db.deliveries.count_documents(
                {"created_at": {"$gte": today_start}, "status": "delivered"}
            )
            total_earnings_pipeline = [
                {"$match": {"status": "delivered"}},
                {"$group": {"_id": None, "total": {"$sum": "$delivery_fee"}}},
            ]
            earnings_res = await db.deliveries.aggregate(
                total_earnings_pipeline
            ).to_list(1)
            self.total_earnings = (
                float(earnings_res[0]["total"]) if earnings_res else 0.0
            )
            enriched_riders = []
            for rider in raw_riders:
                rider_id = rider["user_id"]
                deliveries_count = await db.deliveries.count_documents(
                    {"rider_id": rider_id, "status": "delivered"}
                )
                rider["total_deliveries"] = deliveries_count
                earnings_pipeline = [
                    {"$match": {"rider_id": rider_id, "status": "delivered"}},
                    {"$group": {"_id": None, "total": {"$sum": "$delivery_fee"}}},
                ]
                rider_earnings_res = await db.deliveries.aggregate(
                    earnings_pipeline
                ).to_list(1)
                rider["total_earnings"] = (
                    float(rider_earnings_res[0]["total"]) if rider_earnings_res else 0.0
                )
                active = await db.deliveries.find_one(
                    {
                        "rider_id": rider_id,
                        "status": {"$in": ["accepted", "picked_up", "on_the_way"]},
                    },
                    {"_id": 0},
                )
                rider["is_online"] = active is not None
                rider["active_delivery_status"] = active["status"] if active else ""
                enriched_riders.append(rider)
            self.riders = enriched_riders
        except Exception as e:
            logger.exception(f"Error loading riders: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def load_active_deliveries_logic(self, db):
        cursor = db.deliveries.find(
            {"status": {"$in": ["accepted", "picked_up", "on_the_way"]}}, {"_id": 0}
        ).sort("created_at", -1)
        raw_deliveries = await cursor.to_list(length=50)
        enriched = []
        for d in raw_deliveries:
            rider = await db.users.find_one(
                {"user_id": d.get("rider_id")}, {"name": 1, "_id": 0}
            )
            d["rider_name"] = rider.get("name", "Unknown") if rider else "Unknown"
            order = await db.orders.find_one(
                {"order_id": d.get("order_id")},
                {"restaurant_name": 1, "delivery_address": 1, "_id": 0},
            )
            if order:
                d["restaurant_name"] = order.get("restaurant_name", "")
                d["delivery_address"] = order.get("delivery_address", "")
            else:
                d["restaurant_name"] = ""
                d["delivery_address"] = ""
            accepted_at = d.get("accepted_at")
            if accepted_at:
                d["time_since"] = accepted_at.strftime("%H:%M")
            else:
                created = d.get("created_at")
                d["time_since"] = created.strftime("%H:%M") if created else ""
            enriched.append(d)
        self.active_deliveries = enriched

    @rx.event
    async def load_active_deliveries(self):
        try:
            db = await get_db()
            await self.load_active_deliveries_logic(db)
        except Exception as e:
            logger.exception(f"Error loading active deliveries: {e}")

    @rx.event
    async def load_rider_detail(self, rider_id: str):
        try:
            db = await get_db()
            rider = await db.users.find_one(
                {"user_id": rider_id}, {"password_hash": 0, "_id": 0}
            )
            if rider:
                self.selected_rider = rider
                cursor = db.deliveries.find({"rider_id": rider_id}, {"_id": 0}).sort(
                    "created_at", -1
                )
                history = await cursor.to_list(length=50)
                for h in history:
                    order = await db.orders.find_one(
                        {"order_id": h.get("order_id")},
                        {"restaurant_name": 1, "_id": 0},
                    )
                    h["restaurant_name"] = (
                        order.get("restaurant_name", "") if order else ""
                    )
                self.delivery_history = history
                self.show_rider_detail = True
        except Exception as e:
            logger.exception(f"Error loading rider details: {e}")

    @rx.event
    def toggle_rider_detail(self):
        self.show_rider_detail = not self.show_rider_detail