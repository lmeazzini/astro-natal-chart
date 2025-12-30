"""
Email Theme Constants - "Midnight & Paper" Design System

These color constants match the frontend design system defined in:
- ux/DESIGN_REFERENCE.md
- apps/web/src/styles/globals.css

Note: Email clients don't support CSS variables, so these colors must be
hardcoded in email templates. When updating the design system, ensure
these constants are kept in sync.
"""

# Primary Colors
PRIMARY_DARK = "#1a1f36"  # Deep midnight blue (header/footer backgrounds)
PRIMARY_FOREGROUND = "#d4a84b"  # Stardust gold (headings in dark areas)

# Background Colors
BACKGROUND_CREAM = "#faf9f6"  # Cream paper (body background)
BACKGROUND_WHITE = "#ffffff"  # White (card backgrounds)

# Text Colors
TEXT_PRIMARY = "#1a2035"  # Deep ink (main body text, strong emphasis)
TEXT_SECONDARY = "#606780"  # Muted grey-blue (body text, descriptions)
TEXT_MUTED = "rgba(255, 255, 255, 0.6)"  # Footer text on dark backgrounds

# Accent Colors
ACCENT_GOLD = "#d4a84b"  # Gold (buttons, links, highlights)
ACCENT_GOLD_SHADOW = "rgba(212, 168, 75, 0.3)"  # Gold button shadow

# Border Colors
BORDER_LIGHT = "#e5e7eb"  # Light grey (dividers, card borders)

# Box Shadow
CARD_SHADOW = "rgba(26, 31, 54, 0.08)"  # Subtle card shadow

# Typography
FONT_SERIF = "'Playfair Display', Georgia, serif"
FONT_SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

# Border Radius
BORDER_RADIUS_CARD = "16px"
BORDER_RADIUS_BUTTON = "50px"  # Pill-shaped buttons
BORDER_RADIUS_INPUT = "8px"


def get_email_styles() -> dict:
    """
    Returns a dictionary of common email styles for use in templates.

    Usage:
        styles = get_email_styles()
        f'<div style="{styles["container"]}">'
    """
    return {
        "body": (
            f"font-family: {FONT_SANS}; "
            f"line-height: 1.6; "
            f"color: {TEXT_PRIMARY}; "
            f"background-color: {BACKGROUND_CREAM}; "
            "margin: 0; padding: 20px;"
        ),
        "container": (
            "max-width: 600px; margin: 0 auto; "
            f"background: {BACKGROUND_WHITE}; "
            f"border-radius: {BORDER_RADIUS_CARD}; "
            "overflow: hidden; "
            f"box-shadow: 0 4px 24px {CARD_SHADOW};"
        ),
        "header": (f"background: {PRIMARY_DARK}; padding: 40px 24px; text-align: center;"),
        "header_title": (
            f"font-family: {FONT_SERIF}; color: {PRIMARY_FOREGROUND}; font-size: 24px; margin: 0;"
        ),
        "content": "padding: 40px 32px;",
        "text": (f"font-size: 15px; color: {TEXT_SECONDARY}; margin-bottom: 16px;"),
        "text_strong": f"color: {TEXT_PRIMARY};",
        "button": (
            f"background-color: {ACCENT_GOLD}; "
            f"color: {TEXT_PRIMARY}; "
            f"padding: 16px 32px; "
            "text-decoration: none; "
            f"border-radius: {BORDER_RADIUS_BUTTON}; "
            "display: inline-block; "
            "font-weight: 600; font-size: 15px; "
            f"box-shadow: 0 4px 16px {ACCENT_GOLD_SHADOW};"
        ),
        "alert_box": (
            f"color: {TEXT_SECONDARY}; font-size: 14px; "
            f"background: {BACKGROUND_CREAM}; "
            f"padding: 16px; border-radius: {BORDER_RADIUS_INPUT}; "
            f"border: 1px solid {BORDER_LIGHT};"
        ),
        "divider": (f"border: none; border-top: 1px solid {BORDER_LIGHT}; margin: 28px 0;"),
        "link": f"color: {ACCENT_GOLD}; word-break: break-all;",
        "footer": (f"background: {PRIMARY_DARK}; padding: 24px; text-align: center;"),
        "footer_text": (f"color: {TEXT_MUTED}; font-size: 12px; margin: 0;"),
        "footer_link": f"color: {ACCENT_GOLD};",
    }
