"""
Shared API dependencies and query parameters.
"""

from typing import Annotated

from fastapi import Query

# Supported locales for blog content
SUPPORTED_LOCALES = ["pt-BR", "en-US"]
LOCALE_PATTERN = "^(pt-BR|en-US)$"

# Reusable locale query parameter
# Note: Default value is set with `= None` in the function signature, not in Query()
LocaleQuery = Annotated[
    str | None,
    Query(
        pattern=LOCALE_PATTERN,
        description="Filter by locale (pt-BR or en-US)",
        examples=["pt-BR", "en-US"],
    ),
]
