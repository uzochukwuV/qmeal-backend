import reflex as rx
import logging
from app.utils.db import get_db

logger = logging.getLogger(__name__)


class SettingsState(rx.State):
    platform_settings: dict[str, str | int | float | bool] = {}
    is_saving: bool = False
    save_success: bool = False
    db_status: str = "Connected"
    db_name: str = "qmeal_db"
    api_status: str = "Healthy"
    api_version: str = "v1.0.0"

    @rx.event
    async def load_settings(self):
        try:
            db = await get_db()
            self.db_name = db.name
            settings = await db.admin_settings.find_one({"id": "global"}, {"_id": 0})
            if not settings:
                settings = {
                    "id": "global",
                    "platform_commission_rate": 0.15,
                    "base_delivery_fee": 2.99,
                    "is_platform_active": True,
                }
                await db.admin_settings.insert_one(settings.copy())
            self.platform_settings = settings
            self.save_success = False
        except Exception as e:
            logger.exception(f"Error loading settings: {e}")
            self.db_status = "Disconnected"

    @rx.event
    async def save_settings(self, form_data: dict):
        self.is_saving = True
        self.save_success = False
        yield
        try:
            db = await get_db()
            commission_rate = (
                float(form_data.get("platform_commission_rate", 15)) / 100.0
                if "platform_commission_rate" in form_data
                else 0.15
            )
            base_fee = float(form_data.get("base_delivery_fee", 2.99))
            is_active = bool(form_data.get("is_platform_active", False))
            update_data = {
                "platform_commission_rate": commission_rate,
                "base_delivery_fee": base_fee,
                "is_platform_active": is_active,
            }
            await db.admin_settings.update_one(
                {"id": "global"}, {"$set": update_data}, upsert=True
            )
            self.platform_settings.update(update_data)
            self.save_success = True
            yield rx.toast("Settings saved successfully", duration=3000)
        except Exception as e:
            logger.exception(f"Error saving settings: {e}")
            yield rx.toast("Failed to save settings", duration=3000)
        finally:
            self.is_saving = False