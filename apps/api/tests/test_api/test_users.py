"""
Tests for user profile endpoints (avatar upload, public profile).
"""

import io
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestAvatarUpload:
    """Tests for avatar upload endpoint."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_user: User) -> dict:
        """Get authentication headers for test user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test123!@#",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @staticmethod
    def create_test_image(format_type: str = "jpeg") -> tuple[bytes, str]:
        """
        Create a minimal valid image file for testing.

        Returns:
            Tuple of (image_bytes, content_type)
        """
        if format_type == "jpeg":
            # Minimal valid JPEG (1x1 red pixel)
            image_data = bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46,
                0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
                0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06,
                0x05, 0x08, 0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
                0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
                0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
                0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
                0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
                0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF,
                0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01,
                0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00, 0x01, 0x05,
                0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
                0x07, 0x08, 0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10,
                0x00, 0x02, 0x01, 0x03, 0x03, 0x02, 0x04, 0x03, 0x05, 0x05,
                0x04, 0x04, 0x00, 0x00, 0x01, 0x7D, 0x01, 0x02, 0x03, 0x00,
                0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06, 0x13, 0x51,
                0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
                0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33,
                0x62, 0x72, 0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A,
                0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x34, 0x35, 0x36, 0x37,
                0x38, 0x39, 0x3A, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
                0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x63,
                0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
                0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87,
                0x88, 0x89, 0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98,
                0x99, 0x9A, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9,
                0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8, 0xB9, 0xBA,
                0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xD2,
                0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
                0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2,
                0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA,
                0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5,
                0xDB, 0x20, 0xA8, 0xF1, 0x4C, 0x01, 0xFF, 0xD9
            ])
            return image_data, "image/jpeg"
        elif format_type == "png":
            # Minimal valid PNG (1x1 red pixel)
            image_data = bytes([
                0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
                0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
                0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
                0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
                0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
                0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
                0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
                0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
                0x44, 0xAE, 0x42, 0x60, 0x82
            ])
            return image_data, "image/png"
        elif format_type == "webp":
            # Minimal valid WebP (1x1 pixel)
            image_data = bytes([
                0x52, 0x49, 0x46, 0x46,  # RIFF
                0x24, 0x00, 0x00, 0x00,  # File size - 8
                0x57, 0x45, 0x42, 0x50,  # WEBP
                0x56, 0x50, 0x38, 0x4C,  # VP8L
                0x17, 0x00, 0x00, 0x00,  # Chunk size
                0x2F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            ])
            return image_data, "image/webp"
        raise ValueError(f"Unknown format: {format_type}")

    async def test_upload_avatar_jpeg(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading a valid JPEG avatar."""
        image_data, content_type = self.create_test_image("jpeg")

        response = await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.jpg", io.BytesIO(image_data), content_type)},
        )

        assert response.status_code == 200
        data = response.json()
        assert "avatar_url" in data
        assert data["message"] == "Avatar uploaded successfully"

    async def test_upload_avatar_png(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading a valid PNG avatar."""
        image_data, content_type = self.create_test_image("png")

        response = await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.png", io.BytesIO(image_data), content_type)},
        )

        assert response.status_code == 200
        data = response.json()
        assert "avatar_url" in data

    async def test_upload_avatar_invalid_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading an invalid file type (e.g., GIF)."""
        response = await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.gif", io.BytesIO(b"GIF89a"), "image/gif")},
        )

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    async def test_upload_avatar_mismatched_magic_bytes(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading a file with mismatched content type and magic bytes."""
        # Send PNG magic bytes but claim it's JPEG
        png_data, _ = self.create_test_image("png")

        response = await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.jpg", io.BytesIO(png_data), "image/jpeg")},
        )

        assert response.status_code == 400
        assert "does not match" in response.json()["detail"]

    async def test_upload_avatar_too_large(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading a file that exceeds size limit."""
        # Create 6MB of data (limit is 5MB)
        large_data = b"\xff\xd8\xff" + b"\x00" * (6 * 1024 * 1024)

        response = await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.jpg", io.BytesIO(large_data), "image/jpeg")},
        )

        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    async def test_upload_avatar_unauthorized(self, client: AsyncClient):
        """Test uploading avatar without authentication."""
        image_data, content_type = self.create_test_image("jpeg")

        response = await client.post(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.jpg", io.BytesIO(image_data), content_type)},
        )

        # FastAPI returns 403 when no credentials are provided (not 401)
        assert response.status_code in (401, 403)

    async def test_delete_avatar(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting an avatar."""
        # First upload an avatar
        image_data, content_type = self.create_test_image("jpeg")
        await client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.jpg", io.BytesIO(image_data), content_type)},
        )

        # Then delete it
        response = await client.delete(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
        )

        assert response.status_code == 204


class TestPublicProfile:
    """Tests for public profile endpoint."""

    @pytest.fixture
    async def public_user(
        self, db_session: AsyncSession, test_user_factory
    ) -> User:
        """Create a user with public profile."""
        return await test_user_factory(
            email="public@example.com",
            profile_public=True,
            full_name="Public User",
            bio="Test bio",
        )

    @pytest.fixture
    async def private_user(
        self, db_session: AsyncSession, test_user_factory
    ) -> User:
        """Create a user with private profile."""
        return await test_user_factory(
            email="private@example.com",
            profile_public=False,
            full_name="Private User",
        )

    async def test_get_public_profile_success(
        self, client: AsyncClient, public_user: User
    ):
        """Test getting a public user profile."""
        response = await client.get(f"/api/v1/users/{public_user.id}/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(public_user.id)
        assert data["full_name"] == "Public User"
        assert data["bio"] == "Test bio"
        # Should not include sensitive fields
        assert "email" not in data
        assert "password_hash" not in data

    async def test_get_private_profile_forbidden(
        self, client: AsyncClient, private_user: User
    ):
        """Test getting a private user profile returns 403."""
        response = await client.get(f"/api/v1/users/{private_user.id}/profile")

        assert response.status_code == 403
        assert "private" in response.json()["detail"].lower()

    async def test_get_profile_not_found(self, client: AsyncClient):
        """Test getting a non-existent user profile."""
        fake_id = uuid4()
        response = await client.get(f"/api/v1/users/{fake_id}/profile")

        assert response.status_code == 404


class TestUserProfileUpdate:
    """Tests for user profile update with new fields."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_user: User) -> dict:
        """Get authentication headers for test user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test123!@#",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    async def test_update_user_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating user type."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"user_type": "professional"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_type"] == "professional"

    async def test_update_social_links(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating social links."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "website": "example.com",  # Should auto-add https://
                "instagram": "@testuser",  # Should strip @
                "twitter": "@testhandle",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["website"] == "https://example.com"
        assert data["instagram"] == "testuser"
        assert data["twitter"] == "testhandle"

    async def test_update_specializations(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating specializations."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "user_type": "professional",
                "specializations": ["Natal Charts", "Synastry", "Transits"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Natal Charts" in data["specializations"]
        assert len(data["specializations"]) == 3

    async def test_update_specializations_too_many(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that specializations are limited to 10."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "specializations": [f"Spec {i}" for i in range(15)],
            },
        )

        assert response.status_code == 422  # Validation error
        assert "10" in str(response.json())

    async def test_update_professional_since(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating professional_since year."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "user_type": "professional",
                "professional_since": 2015,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["professional_since"] == 2015

    async def test_update_professional_since_future_year(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that professional_since cannot be in the future."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "professional_since": 2050,
            },
        )

        assert response.status_code == 422  # Validation error
