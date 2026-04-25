import reflex as rx
import bcrypt
import jwt
import os
import uuid
import logging
from datetime import datetime, timezone
from app.utils.db import get_db, seed_data

JWT_SECRET = os.environ.get("JWT_SECRET", "qmeal-super-secret-key-change-in-production")


class AuthState(rx.State):
    is_authenticated: bool = False
    user_id: str = ""
    user_email: str = ""
    user_name: str = ""
    user_role: str = ""
    token: str = ""
    login_error: str = ""
    is_loading: bool = False

    @rx.event
    async def check_auth(self):
        try:
            await seed_data()
        except Exception as e:
            logging.exception(f"Seed data check failed: {e}")
        if self.token:
            try:
                payload = jwt.decode(self.token, JWT_SECRET, algorithms=["HS256"])
                self.is_authenticated = True
                return rx.redirect("/dashboard")
            except Exception:
                logging.exception("Unexpected error")
                self.logout()

    @rx.event
    async def login(self, form_data: dict):
        self.is_loading = True
        self.login_error = ""
        yield
        email = form_data.get("email", "")
        password = form_data.get("password", "")
        if not email or not password:
            self.login_error = "Email and password are required."
            self.is_loading = False
            return
        try:
            db = await get_db()
            user = await db.users.find_one({"email": email.lower()})
            if user and bcrypt.checkpw(
                password.encode("utf-8"), user.get("password_hash", "").encode("utf-8")
            ):
                self.user_id = user.get("user_id", "")
                self.user_email = user.get("email", "")
                self.user_name = user.get("name", "")
                self.user_role = user.get("role", "customer")
                self.is_authenticated = True
                payload = {
                    "user_id": self.user_id,
                    "exp": datetime.now(timezone.utc).timestamp() + 24 * 7 * 3600,
                }
                self.token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
                self.is_loading = False
                yield rx.redirect("/dashboard")
                return
            else:
                self.login_error = "Invalid credentials."
        except Exception as e:
            logging.exception(f"Login error: {e}")
            self.login_error = "Connection error."
        self.is_loading = False

    @rx.event
    async def register_admin(self, form_data: dict):
        self.is_loading = True
        self.login_error = ""
        yield
        email = form_data.get("email", "")
        password = form_data.get("password", "")
        name = form_data.get("name", "")
        secret_key = form_data.get("secret_key", "")
        if secret_key != "qmeal_admin_secret_2024":
            self.login_error = "Invalid admin secret key."
            self.is_loading = False
            return
        if not email or not password or (not name):
            self.login_error = "All fields are required."
            self.is_loading = False
            return
        try:
            db = await get_db()
            existing = await db.users.find_one({"email": email.lower()})
            if existing:
                self.login_error = "Email already registered."
                self.is_loading = False
                return
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user_doc = {
                "user_id": user_id,
                "email": email.lower(),
                "name": name,
                "password_hash": hashed_password,
                "role": "admin",
                "created_at": datetime.now(timezone.utc),
            }
            await db.users.insert_one(user_doc)
            self.user_id = user_id
            self.user_email = email
            self.user_name = name
            self.user_role = "admin"
            self.is_authenticated = True
            payload = {
                "user_id": self.user_id,
                "exp": datetime.now(timezone.utc).timestamp() + 24 * 7 * 3600,
            }
            self.token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            self.is_loading = False
            yield rx.redirect("/dashboard")
            return
        except Exception as e:
            logging.exception(f"Register admin error: {e}")
            self.login_error = "Registration failed."
        self.is_loading = False

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.user_id = ""
        self.user_email = ""
        self.user_name = ""
        self.user_role = ""
        self.token = ""
        return rx.redirect("/")