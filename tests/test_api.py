"""
Integration tests for FastAPI endpoints.
"""
import pytest
from httpx import AsyncClient


class TestProductEndpoints:
    """Tests for product API endpoints."""



    @pytest.mark.asyncio
    async def test_create_product_missing_required_field(self, async_client):
        payload = {
            "name": "Incomplete Product",
            "category": "Test"
        }

        response = await async_client.post("/api/v1/products/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_product_negative_price(self, async_client):
        payload = {
            "name": "Test",
            "category": "Test",
            "description": "Test",
            "price": -50.00
        }

        response = await async_client.post("/api/v1/products/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_product_invalid_url(self, async_client):
        payload = {
            "name": "Test",
            "category": "Test",
            "description": "Test",
            "price": 50.00,
            "thumbnail_url": "not-a-url"
        }

        response = await async_client.post("/api/v1/products/", json=payload)
        assert response.status_code == 422


    @pytest.mark.asyncio
    async def test_search_products_missing_query(self, async_client):
        response = await async_client.get("/api/v1/products/search/")
        assert response.status_code == 422


    @pytest.mark.asyncio
    async def test_update_product_invalid_price(self, async_client):
        payload = {"price": -50.00}
        response = await async_client.put("/api/v1/products/some-id", json=payload)
        assert response.status_code == 422




class TestGUIRoutes:
    """Tests for GUI/template routes."""

    @pytest.mark.asyncio
    async def test_home_page(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_login_page(self, async_client):
        response = await async_client.get("/login")
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_json_body(self, async_client):
        response = await async_client.post(
            "/api/v1/products/",
            content=b"invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [400, 422]



    @pytest.mark.asyncio
    async def test_method_not_allowed(self, async_client):
        response = await async_client.patch("/api/v1/products/")
        assert response.status_code in [404, 405]