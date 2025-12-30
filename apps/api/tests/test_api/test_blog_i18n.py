"""
Tests for blog internationalization (i18n) functionality.

Tests cover:
- Locale filtering in API endpoints
- Translation linking between posts
- Translation key uniqueness validation
- Cache invalidation for locale-specific data
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blog_post import BlogPost
from app.repositories.blog_repository import BlogRepository
from app.schemas.blog import BlogPostCreate
from app.services.blog_service import BlogService


@pytest.fixture
async def blog_post_factory(db_session: AsyncSession):
    """Factory to create test blog posts."""

    async def _create_post(
        slug: str = "test-post",
        locale: str = "pt-BR",
        translation_key: str | None = None,
        title: str = "Test Post",
        content: str = "Test content for the blog post.",
        excerpt: str = "Test excerpt",
        category: str = "fundamentals",
        tags: list[str] | None = None,
        published: bool = True,
        author_id: UUID | None = None,
    ) -> BlogPost:
        post = BlogPost(
            id=uuid4(),
            slug=slug,
            locale=locale,
            translation_key=translation_key,
            title=title,
            content=content,
            excerpt=excerpt,
            category=category,
            tags=tags or ["test"],
            read_time_minutes=1,
            published_at=datetime.now(UTC) if published else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            author_id=author_id,
        )
        db_session.add(post)
        await db_session.commit()
        await db_session.refresh(post)
        return post

    return _create_post


# ===== Repository Tests =====


class TestBlogRepositoryLocaleFiltering:
    """Tests for BlogRepository locale filtering methods."""

    @pytest.mark.asyncio
    async def test_get_published_filters_by_locale(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that get_published filters posts by locale."""
        # Create posts in different locales
        await blog_post_factory(slug="post-pt", locale="pt-BR", title="Post em Português")
        await blog_post_factory(slug="post-en", locale="en-US", title="Post in English")

        repo = BlogRepository(db_session)

        # Get only Portuguese posts
        pt_posts, pt_count = await repo.get_published(locale="pt-BR")
        assert pt_count == 1
        assert pt_posts[0].locale == "pt-BR"
        assert pt_posts[0].title == "Post em Português"

        # Get only English posts
        en_posts, en_count = await repo.get_published(locale="en-US")
        assert en_count == 1
        assert en_posts[0].locale == "en-US"
        assert en_posts[0].title == "Post in English"

        # Get all posts (no locale filter)
        all_posts, all_count = await repo.get_published()
        assert all_count == 2

    @pytest.mark.asyncio
    async def test_get_by_slug_with_locale(self, db_session: AsyncSession, blog_post_factory):
        """Test that get_by_slug can filter by locale."""
        # Create posts with same slug but different locales
        await blog_post_factory(
            slug="saturn-mythology", locale="pt-BR", title="Saturno - Mitologia"
        )
        await blog_post_factory(slug="saturn-mythology", locale="en-US", title="Saturn - Mythology")

        repo = BlogRepository(db_session)

        # Get Portuguese version
        pt_post = await repo.get_by_slug("saturn-mythology", locale="pt-BR")
        assert pt_post is not None
        assert pt_post.title == "Saturno - Mitologia"

        # Get English version
        en_post = await repo.get_by_slug("saturn-mythology", locale="en-US")
        assert en_post is not None
        assert en_post.title == "Saturn - Mythology"

    @pytest.mark.asyncio
    async def test_get_translations(self, db_session: AsyncSession, blog_post_factory):
        """Test fetching all translations of a post."""
        translation_key = "saturn-mythology"

        # Create linked translations
        await blog_post_factory(
            slug="saturno-mitologia",
            locale="pt-BR",
            translation_key=translation_key,
            title="Saturno - Mitologia",
        )
        await blog_post_factory(
            slug="saturn-mythology",
            locale="en-US",
            translation_key=translation_key,
            title="Saturn - Mythology",
        )

        repo = BlogRepository(db_session)

        # Get all translations
        translations = await repo.get_translations(translation_key)
        assert len(translations) == 2

        # Get translations excluding one locale
        pt_excluded = await repo.get_translations(translation_key, exclude_locale="pt-BR")
        assert len(pt_excluded) == 1
        assert pt_excluded[0].locale == "en-US"

    @pytest.mark.asyncio
    async def test_get_by_translation_key_and_locale(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test fetching post by translation key and locale."""
        translation_key = "test-key"

        await blog_post_factory(slug="test-pt", locale="pt-BR", translation_key=translation_key)
        await blog_post_factory(slug="test-en", locale="en-US", translation_key=translation_key)

        repo = BlogRepository(db_session)

        # Should find the Portuguese post
        pt_post = await repo.get_by_translation_key_and_locale(translation_key, "pt-BR")
        assert pt_post is not None
        assert pt_post.slug == "test-pt"

        # Should not find a non-existent combination
        missing = await repo.get_by_translation_key_and_locale("non-existent", "pt-BR")
        assert missing is None

    @pytest.mark.asyncio
    async def test_get_categories_with_count_filters_by_locale(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that category counts are filtered by locale."""
        await blog_post_factory(slug="pt-1", locale="pt-BR", category="fundamentals")
        await blog_post_factory(slug="pt-2", locale="pt-BR", category="fundamentals")
        await blog_post_factory(slug="en-1", locale="en-US", category="fundamentals")

        repo = BlogRepository(db_session)

        # Portuguese locale should have 2 posts in fundamentals
        pt_categories = await repo.get_categories_with_count(locale="pt-BR")
        pt_fundamentals = next((c for c in pt_categories if c[0] == "fundamentals"), None)
        assert pt_fundamentals is not None
        assert pt_fundamentals[1] == 2

        # English locale should have 1 post in fundamentals
        en_categories = await repo.get_categories_with_count(locale="en-US")
        en_fundamentals = next((c for c in en_categories if c[0] == "fundamentals"), None)
        assert en_fundamentals is not None
        assert en_fundamentals[1] == 1

    @pytest.mark.asyncio
    async def test_get_popular_tags_filters_by_locale(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that popular tags are filtered by locale."""
        await blog_post_factory(slug="pt-1", locale="pt-BR", tags=["mythology", "saturn"])
        await blog_post_factory(slug="pt-2", locale="pt-BR", tags=["mythology"])
        await blog_post_factory(slug="en-1", locale="en-US", tags=["mythology"])

        repo = BlogRepository(db_session)

        # Portuguese locale: mythology=2, saturn=1
        pt_tags = await repo.get_popular_tags(locale="pt-BR")
        pt_mythology = next((t for t in pt_tags if t[0] == "mythology"), None)
        assert pt_mythology is not None
        assert pt_mythology[1] == 2

        # English locale: mythology=1
        en_tags = await repo.get_popular_tags(locale="en-US")
        en_mythology = next((t for t in en_tags if t[0] == "mythology"), None)
        assert en_mythology is not None
        assert en_mythology[1] == 1


# ===== Service Tests =====


class TestBlogServiceI18n:
    """Tests for BlogService internationalization features."""

    @pytest.mark.asyncio
    async def test_create_post_validates_translation_key_uniqueness(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that creating a post with duplicate translation_key+locale fails."""
        translation_key = "unique-key"

        # Create first post
        await blog_post_factory(slug="first-post", locale="pt-BR", translation_key=translation_key)

        service = BlogService(db_session)

        # Try to create another post with same translation_key and locale
        with pytest.raises(ValueError) as exc_info:
            await service.create_post(
                BlogPostCreate(
                    title="Duplicate Post",
                    content="Content",
                    excerpt="Excerpt",
                    category="test",
                    locale="pt-BR",
                    translation_key=translation_key,
                )
            )

        assert "already exists for locale" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_post_allows_same_translation_key_different_locale(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that same translation_key can be used with different locales."""
        translation_key = "shared-key"

        # Create Portuguese post
        await blog_post_factory(slug="post-pt", locale="pt-BR", translation_key=translation_key)

        service = BlogService(db_session)

        # Should successfully create English version
        post = await service.create_post(
            BlogPostCreate(
                title="English Post",
                content="Content",
                excerpt="Excerpt",
                category="test",
                locale="en-US",
                translation_key=translation_key,
            )
        )

        assert post.locale == "en-US"
        assert post.translation_key == translation_key

    @pytest.mark.asyncio
    async def test_get_post_by_slug_returns_available_translations(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that post detail includes available translations."""
        translation_key = "linked-post"

        await blog_post_factory(
            slug="post-pt",
            locale="pt-BR",
            translation_key=translation_key,
            title="Post em Português",
        )
        await blog_post_factory(
            slug="post-en",
            locale="en-US",
            translation_key=translation_key,
            title="Post in English",
        )

        service = BlogService(db_session)

        # Get Portuguese post
        pt_post = await service.get_post_by_slug("post-pt", locale="pt-BR")
        assert pt_post is not None
        assert pt_post.available_translations is not None
        assert len(pt_post.available_translations) == 1
        assert pt_post.available_translations[0].locale == "en-US"
        assert pt_post.available_translations[0].slug == "post-en"


# ===== API Endpoint Tests =====


class TestBlogAPILocaleFiltering:
    """Tests for blog API endpoints with locale filtering."""

    @pytest.mark.asyncio
    async def test_list_posts_filters_by_locale(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/posts with locale filter."""
        await blog_post_factory(slug="pt-post", locale="pt-BR", title="Post PT")
        await blog_post_factory(slug="en-post", locale="en-US", title="Post EN")

        # Filter by Portuguese
        response = await client.get("/api/v1/blog/posts", params={"locale": "pt-BR"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["locale"] == "pt-BR"

        # Filter by English
        response = await client.get("/api/v1/blog/posts", params={"locale": "en-US"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["locale"] == "en-US"

    @pytest.mark.asyncio
    async def test_list_posts_returns_all_without_locale_filter(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/posts returns all posts without locale filter."""
        await blog_post_factory(slug="pt-post", locale="pt-BR")
        await blog_post_factory(slug="en-post", locale="en-US")

        response = await client.get("/api/v1/blog/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_posts_rejects_invalid_locale(self, client: AsyncClient):
        """Test GET /blog/posts rejects invalid locale values."""
        response = await client.get("/api/v1/blog/posts", params={"locale": "invalid"})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_post_with_locale(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/posts/{slug} with locale parameter."""
        # Create posts with same slug in different locales
        await blog_post_factory(slug="shared-slug", locale="pt-BR", title="Título em Português")
        await blog_post_factory(slug="shared-slug", locale="en-US", title="Title in English")

        # Get Portuguese version
        response = await client.get("/api/v1/blog/posts/shared-slug", params={"locale": "pt-BR"})
        assert response.status_code == 200
        assert response.json()["title"] == "Título em Português"

        # Get English version
        response = await client.get("/api/v1/blog/posts/shared-slug", params={"locale": "en-US"})
        assert response.status_code == 200
        assert response.json()["title"] == "Title in English"

    @pytest.mark.asyncio
    async def test_get_post_includes_available_translations(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/posts/{slug} includes available_translations."""
        translation_key = "translated-post"

        await blog_post_factory(
            slug="post-pt",
            locale="pt-BR",
            translation_key=translation_key,
            title="Post PT",
        )
        await blog_post_factory(
            slug="post-en",
            locale="en-US",
            translation_key=translation_key,
            title="Post EN",
        )

        response = await client.get("/api/v1/blog/posts/post-pt", params={"locale": "pt-BR"})
        assert response.status_code == 200
        data = response.json()

        assert data["available_translations"] is not None
        assert len(data["available_translations"]) == 1
        assert data["available_translations"][0]["locale"] == "en-US"
        assert data["available_translations"][0]["slug"] == "post-en"

    @pytest.mark.asyncio
    async def test_get_metadata_filters_by_locale(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/metadata with locale filter."""
        await blog_post_factory(slug="pt-1", locale="pt-BR", category="fundamentals")
        await blog_post_factory(slug="pt-2", locale="pt-BR", category="fundamentals")
        await blog_post_factory(slug="en-1", locale="en-US", category="fundamentals")

        # Get Portuguese metadata
        response = await client.get("/api/v1/blog/metadata", params={"locale": "pt-BR"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_posts"] == 2

        # Get English metadata
        response = await client.get("/api/v1/blog/metadata", params={"locale": "en-US"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_posts"] == 1

    @pytest.mark.asyncio
    async def test_get_recent_posts_filters_by_locale(
        self, client: AsyncClient, db_session: AsyncSession, blog_post_factory
    ):
        """Test GET /blog/recent with locale filter."""
        await blog_post_factory(slug="pt-post", locale="pt-BR")
        await blog_post_factory(slug="en-post", locale="en-US")

        response = await client.get("/api/v1/blog/recent", params={"locale": "pt-BR"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["locale"] == "pt-BR"


# ===== Slug Uniqueness Tests =====


class TestSlugLocaleUniqueness:
    """Tests for slug uniqueness per locale."""

    @pytest.mark.asyncio
    async def test_same_slug_different_locales_allowed(
        self, db_session: AsyncSession, blog_post_factory
    ):
        """Test that same slug can exist in different locales."""
        # This should work without errors
        post1 = await blog_post_factory(slug="my-post", locale="pt-BR")
        post2 = await blog_post_factory(slug="my-post", locale="en-US")

        assert post1.slug == post2.slug
        assert post1.locale != post2.locale

    @pytest.mark.asyncio
    async def test_slug_exists_checks_locale(self, db_session: AsyncSession, blog_post_factory):
        """Test that slug_exists considers locale."""
        await blog_post_factory(slug="existing-post", locale="pt-BR")

        repo = BlogRepository(db_session)

        # Same slug, same locale - should exist
        assert await repo.slug_exists("existing-post", locale="pt-BR") is True

        # Same slug, different locale - should not exist
        assert await repo.slug_exists("existing-post", locale="en-US") is False
