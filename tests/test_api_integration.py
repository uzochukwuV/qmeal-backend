import pytest
import pytest_asyncio
import httpx
from fastapi import FastAPI
from app.api.routes import api_router
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime, timezone

test_app = FastAPI()
test_app.include_router(api_router)


@pytest_asyncio.fixture(autouse=True)
async def mock_db(monkeypatch):
    """Mock the MongoDB layer and seed it with test data."""
    client = AsyncMongoMockClient()
    test_db = client["qmeal_db"]
    restaurants = [
        {
            "restaurant_id": f"rest_00{i + 1}",
            "name": [
                "Bella Italia",
                "Tokyo Ramen House",
                "Burger Republic",
                "Spice Garden",
                "Le Petit Bistro",
                "Taco Fiesta",
                "Dragon Palace",
                "Mediterranean Grill",
            ][i],
            "description": "Test description",
            "cuisine_type": [
                "Italian",
                "Japanese",
                "American",
                "Indian",
                "French",
                "Mexican",
                "Chinese",
                "Mediterranean",
            ][i],
            "rating": [4.7, 4.8, 4.5, 4.6, 4.9, 4.4, 4.3, 4.6][i],
            "review_count": 100,
            "price_level": [2, 2, 1, 2, 4, 1, 2, 3][i],
            "image_url": "/placeholder.svg",
            "address": f"{i + 1} Test St",
            "latitude": 40.0,
            "longitude": -70.0,
            "delivery_time_min": 20,
            "delivery_time_max": 40,
            "delivery_fee": 2.99,
            "is_open": True,
            "created_at": datetime.now(timezone.utc),
        }
        for i in range(8)
    ]
    await test_db.restaurants.insert_many(restaurants)
    menu_items = []
    for i in range(8):
        rest_id = f"rest_00{i + 1}"
        for j in range(5):
            item_name = f"Item {j + 1} from {rest_id}"
            if rest_id == "rest_003" and j == 0:
                item_name = "Classic Smash Burger"
            menu_items.append(
                {
                    "item_id": f"item_{rest_id}_{j}",
                    "restaurant_id": rest_id,
                    "name": item_name,
                    "description": "Delicious test food",
                    "price": 10.99 + j,
                    "category": "Main",
                    "is_available": True,
                    "is_popular": j == 0,
                }
            )
    await test_db.menu_items.insert_many(menu_items)
    monkeypatch.setattr("app.api.routes.db", test_db)
    monkeypatch.setattr("app.utils.db.db", test_db)
    yield test_db
    client.close()


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test that the public /api/health endpoint returns 200 OK and 'healthy' status."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_cuisines_publicly():
    """Test that the public /api/cuisines endpoint returns a list of cuisines without auth."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/cuisines")
        assert response.status_code == 200
        data = response.json()
        assert "cuisines" in data
        assert isinstance(data["cuisines"], list)
        assert len(data["cuisines"]) > 0
        assert "Italian" in data["cuisines"]


@pytest.mark.asyncio
async def test_get_restaurants_publicly_with_filters():
    """Test fetching restaurants publicly, including filter parameters."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/restaurants?cuisine=Italian")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["cuisine_type"] == "Italian"
        response = await client.get("/api/restaurants?min_rating=4.8")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any((r["name"] == "Tokyo Ramen House" for r in data))
        response = await client.get("/api/restaurants?sort_by=price")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["price_level"] == 1


@pytest.mark.asyncio
async def test_get_restaurant_detail_publicly():
    """Test fetching a specific restaurant detail page without authentication."""
    restaurant_id = "rest_001"
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/restaurants/{restaurant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["restaurant_id"] == restaurant_id
        assert data["name"] == "Bella Italia"


@pytest.mark.asyncio
async def test_get_restaurant_menu_publicly():
    """Test fetching a specific restaurant menu without authentication."""
    restaurant_id = "rest_003"
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/restaurants/{restaurant_id}/menu")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all((item["is_available"] for item in data))
        assert any((item["name"] == "Classic Smash Burger" for item in data))


@pytest.mark.asyncio
async def test_get_restaurant_reviews_publicly():
    """Test fetching reviews for a restaurant without authentication."""
    restaurant_id = "rest_001"
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/restaurants/{restaurant_id}/reviews")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        non_existent_id = "rest_999"
        response = await client.get(f"/api/restaurants/{non_existent_id}/reviews")
        assert response.status_code == 200
        data = response.json()
        assert data == []