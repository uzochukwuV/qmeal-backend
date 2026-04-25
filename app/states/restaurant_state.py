import reflex as rx
from typing import Any, Optional
import logging
from app.utils.db import get_db
import uuid

logger = logging.getLogger(__name__)


class RestaurantState(rx.State):
    restaurants: list[dict[str, str | int | float | bool | list | dict]] = []
    selected_restaurant: dict[str, str | int | float | bool | list | dict] = {}
    menu_items: list[dict[str, str | int | float | bool | list | dict]] = []
    reviews: list[dict[str, str | int | float | bool | list | dict]] = []
    search_query: str = ""
    cuisine_filter: str = ""
    cuisines: list[str] = []
    is_loading: bool = False
    show_edit_modal: bool = False
    show_add_menu_modal: bool = False
    edit_form: dict[str, str | int | float | bool | list | dict] = {}
    menu_form: dict[str, str | int | float | bool | list | dict] = {}

    @rx.event
    async def load_restaurants(self):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            query = {}
            if self.search_query:
                query["name"] = {"$regex": self.search_query, "$options": "i"}
            if self.cuisine_filter:
                query["cuisine_type"] = self.cuisine_filter
            cursor = db.restaurants.find(query, {"_id": 0})
            self.restaurants = await cursor.to_list(length=100)
            cuisines = await db.restaurants.distinct("cuisine_type")
            self.cuisines = cuisines
        except Exception as e:
            logger.exception(f"Error loading restaurants: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def load_restaurant_detail(self):
        self.is_loading = True
        yield
        try:
            restaurant_id = self.router.page.params.get("restaurant_id", "")
            if not restaurant_id:
                return
            db = await get_db()
            self.selected_restaurant = (
                await db.restaurants.find_one(
                    {"restaurant_id": restaurant_id}, {"_id": 0}
                )
                or {}
            )
            self.edit_form = self.selected_restaurant.copy()
            menu_cursor = db.menu_items.find(
                {"restaurant_id": restaurant_id}, {"_id": 0}
            )
            self.menu_items = await menu_cursor.to_list(length=200)
            reviews_cursor = db.reviews.find(
                {"restaurant_id": restaurant_id}, {"_id": 0}
            )
            self.reviews = await reviews_cursor.to_list(length=100)
        except Exception as e:
            logger.exception(f"Error loading restaurant details: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def update_restaurant(self, form_data: dict):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            restaurant_id = self.selected_restaurant.get("restaurant_id")
            if restaurant_id:
                update_data = {
                    "name": form_data.get("name"),
                    "description": form_data.get("description"),
                    "cuisine_type": form_data.get("cuisine_type"),
                    "address": form_data.get("address"),
                    "delivery_time_min": int(form_data.get("delivery_time_min", 0)),
                    "delivery_time_max": int(form_data.get("delivery_time_max", 0)),
                    "delivery_fee": float(form_data.get("delivery_fee", 0.0)),
                }
                await db.restaurants.update_one(
                    {"restaurant_id": restaurant_id}, {"$set": update_data}
                )
                self.show_edit_modal = False
                await self.load_restaurant_detail()
        except Exception as e:
            logger.exception(f"Error updating restaurant: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def add_menu_item(self, form_data: dict):
        self.is_loading = True
        yield
        try:
            db = await get_db()
            restaurant_id = self.selected_restaurant.get("restaurant_id")
            if restaurant_id:
                new_item = {
                    "item_id": f"item_{uuid.uuid4().hex[:12]}",
                    "restaurant_id": restaurant_id,
                    "name": form_data.get("name"),
                    "description": form_data.get("description"),
                    "price": float(form_data.get("price", 0.0)),
                    "category": form_data.get("category"),
                    "is_available": bool(form_data.get("is_available", True)),
                    "is_popular": bool(form_data.get("is_popular", False)),
                }
                await db.menu_items.insert_one(new_item)
                self.show_add_menu_modal = False
                await self.load_restaurant_detail()
        except Exception as e:
            logger.exception(f"Error adding menu item: {e}")
        finally:
            self.is_loading = False

    @rx.event
    async def delete_menu_item(self, item_id: str):
        try:
            db = await get_db()
            await db.menu_items.delete_one({"item_id": item_id})
            await self.load_restaurant_detail()
        except Exception as e:
            logger.exception(f"Error deleting menu item: {e}")

    @rx.event
    async def toggle_menu_availability(self, item_id: str, current_status: bool):
        try:
            db = await get_db()
            await db.menu_items.update_one(
                {"item_id": item_id}, {"$set": {"is_available": not current_status}}
            )
            await self.load_restaurant_detail()
        except Exception as e:
            logger.exception(f"Error toggling menu availability: {e}")

    @rx.event
    async def toggle_restaurant_status(self, restaurant_id: str, current_status: bool):
        try:
            db = await get_db()
            await db.restaurants.update_one(
                {"restaurant_id": restaurant_id},
                {"$set": {"is_open": not current_status}},
            )
            await self.load_restaurants()
            if self.selected_restaurant.get("restaurant_id") == restaurant_id:
                await self.load_restaurant_detail()
        except Exception as e:
            logger.exception(f"Error toggling restaurant status: {e}")

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        return RestaurantState.load_restaurants

    @rx.event
    def set_cuisine_filter(self, cuisine: str):
        self.cuisine_filter = cuisine
        return RestaurantState.load_restaurants

    @rx.event
    def toggle_edit_modal(self):
        self.show_edit_modal = not self.show_edit_modal

    @rx.event
    def toggle_add_menu_modal(self):
        self.show_add_menu_modal = not self.show_add_menu_modal