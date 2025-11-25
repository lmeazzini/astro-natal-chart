"""
SEO endpoints for sitemap.xml and RSS feed.
"""

from datetime import UTC, datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.repositories.blog_repository import BlogRepository

router = APIRouter(prefix="/seo", tags=["seo"])


def get_base_url(request: Request) -> str:
    """Get the base URL from the request."""
    # In production, use the configured frontend URL
    # In development, use the request's host
    return (
        str(settings.FRONTEND_URL).rstrip("/")
        if settings.FRONTEND_URL
        else str(request.base_url).rstrip("/")
    )


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Generate sitemap.xml for SEO.

    Includes:
    - Static pages (home, about, etc.)
    - Blog posts
    - Public charts (if any)
    """
    base_url = get_base_url(request)

    # Create XML structure
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add static pages
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/blog", "priority": "0.9", "changefreq": "daily"},
        {"loc": "/sobre", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "/privacidade", "priority": "0.5", "changefreq": "yearly"},
        {"loc": "/termos", "priority": "0.5", "changefreq": "yearly"},
    ]

    for page in static_pages:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{base_url}{page['loc']}"
        changefreq = SubElement(url, "changefreq")
        changefreq.text = page["changefreq"]
        priority = SubElement(url, "priority")
        priority.text = page["priority"]

    # Add blog posts
    repo = BlogRepository(db)
    posts = await repo.get_all_published_for_sitemap()

    for post in posts:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{base_url}/blog/{post.slug}"
        lastmod = SubElement(url, "lastmod")
        lastmod.text = post.updated_at.strftime("%Y-%m-%d")
        changefreq = SubElement(url, "changefreq")
        changefreq.text = "weekly"
        priority = SubElement(url, "priority")
        priority.text = "0.8"

    # Generate XML string
    xml_string = tostring(urlset, encoding="unicode")
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

    return Response(
        content=xml_declaration + xml_string,
        media_type="application/xml",
    )


@router.get("/rss.xml", response_class=Response)
async def rss_feed(
    request: Request,
    full_content: bool = False,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Generate RSS feed for blog posts.

    Returns the 20 most recent published posts.

    Args:
        full_content: If True, includes full post content instead of just excerpt
    """
    base_url = get_base_url(request)

    # Create RSS structure
    rss = Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

    channel = SubElement(rss, "channel")

    # Channel metadata
    title = SubElement(channel, "title")
    title.text = "Astro Natal Chart Blog"

    link = SubElement(channel, "link")
    link.text = f"{base_url}/blog"

    description = SubElement(channel, "description")
    description.text = "Artigos sobre astrologia natal, mapas astrais e autoconhecimento."

    language = SubElement(channel, "language")
    language.text = "pt-BR"

    # Atom self-link
    atom_link = SubElement(channel, "atom:link")
    atom_link.set("href", f"{base_url}/api/v1/seo/rss.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    last_build = SubElement(channel, "lastBuildDate")
    last_build.text = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Get recent posts
    repo = BlogRepository(db)
    posts = await repo.get_all_published_for_rss(limit=20)

    for post in posts:
        item = SubElement(channel, "item")

        item_title = SubElement(item, "title")
        item_title.text = post.title

        item_link = SubElement(item, "link")
        item_link.text = f"{base_url}/blog/{post.slug}"

        item_description = SubElement(item, "description")
        item_description.text = post.content if full_content else post.excerpt

        # Add content:encoded for full content (RSS best practice)
        if full_content:
            content_encoded = SubElement(item, "content:encoded")
            content_encoded.text = post.content

        item_guid = SubElement(item, "guid")
        item_guid.text = f"{base_url}/blog/{post.slug}"
        item_guid.set("isPermaLink", "true")

        if post.published_at:
            pub_date = SubElement(item, "pubDate")
            pub_date.text = post.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")

        if post.category:
            category = SubElement(item, "category")
            category.text = post.category

        if post.author:
            author = SubElement(item, "author")
            author.text = post.author.full_name or post.author.email

    # Generate XML string
    xml_string = tostring(rss, encoding="unicode")
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

    return Response(
        content=xml_declaration + xml_string,
        media_type="application/rss+xml",
    )


@router.get("/robots.txt", response_class=Response)
async def robots_txt(request: Request) -> Response:
    """
    Generate robots.txt for search engine crawlers.
    """
    base_url = get_base_url(request)

    content = f"""User-agent: *
Allow: /
Allow: /blog
Allow: /blog/*

Disallow: /app
Disallow: /dashboard
Disallow: /charts
Disallow: /api

Sitemap: {base_url}/api/v1/seo/sitemap.xml
"""

    return Response(content=content, media_type="text/plain")
