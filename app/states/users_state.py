import reflex as rx
import logging
from app.utils.db import get_db

logger = logging.getLogger(__name__)


class UsersState(rx.State):
    users: list[dict[str, str | int | float | bool | list | dict]] = []
    role_filter: str = "all"
    search_query: str = ""
    is_loading: bool = False
    user_counts: dict[str, int] = {
        "all": 0,
        "customer": 0,
        "owner": 0,
        "rider": 0,
        "admin": 0,
    }
    selected_user: dict[str, str | int | float | bool | list | dict] = {}
    show_user_modal: bool = False

    @rx.event
    async def load_users(self):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            query = {}
            if self.role_filter != "all":
                query["role"] = self.role_filter
            if self.search_query:
                query["$or"] = [
                    {"name": {"$regex": self.search_query, "$options": "i"}},
                    {"email": {"$regex": self.search_query, "$options": "i"}},
                ]
            cursor = db.users.find(query, {"password_hash": 0, "_id": 0}).sort(
                "created_at", -1
            )
            raw_users = await cursor.to_list(length=200)
            self.users = raw_users
            pipeline = [{"$group": {"_id": "$role", "count": {"$sum": 1}}}]
            counts_result = await db.users.aggregate(pipeline).to_list(None)
            counts = {"all": 0, "customer": 0, "owner": 0, "rider": 0, "admin": 0}
            counts["all"] = sum((c["count"] for c in counts_result))
            for c in counts_result:
                counts[c["_id"]] = c["count"]
            self.user_counts = counts
        except Exception as e:
            logger.exception(f"Error loading users: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def update_user_role(self, user_id: str, new_role: str):
        try:
            db = await get_db()
            await db.users.update_one(
                {"user_id": user_id}, {"$set": {"role": new_role}}
            )
            await self.load_users()
        except Exception as e:
            logger.exception(f"Error updating role: {e}")

    @rx.event
    def set_role_filter(self, role: str):
        self.role_filter = role
        return UsersState.load_users

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        return UsersState.load_users

    @rx.event
    async def view_user(self, user_id: str):
        try:
            db = await get_db()
            user = await db.users.find_one(
                {"user_id": user_id}, {"password_hash": 0, "_id": 0}
            )
            if user:
                self.selected_user = user
                self.show_user_modal = True
        except Exception as e:
            logger.exception(f"Error loading user details: {e}")

    @rx.event
    def toggle_user_modal(self):
        self.show_user_modal = not self.show_user_modal