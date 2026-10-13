"""Shared limit/offset paging for list endpoints.

The response body stays a plain JSON list, exactly as before, so existing
pages keep working. The total number of matching rows is returned in the
``X-Total-Count`` header.

``limit`` defaults to DEFAULT_LIMIT and can never exceed MAX_LIMIT, so one
request can no longer pull an entire table.
"""

from dataclasses import dataclass

from fastapi import Query, Response

DEFAULT_LIMIT = 500
MAX_LIMIT = 1000

TOTAL_COUNT_HEADER = "X-Total-Count"


@dataclass(frozen=True)
class PageParams:
    limit: int
    offset: int


def get_page_params(
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description="Maximum number of items to return.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of items to skip.",
    ),
) -> PageParams:
    return PageParams(limit=limit, offset=offset)


def paginate(query, page: PageParams, response: Response) -> list:
    """Apply paging to a SQLAlchemy query and return the rows."""

    response.headers[TOTAL_COUNT_HEADER] = str(
        query.order_by(None).count()
    )

    if not query._order_by_clauses:
        # Paging needs a stable order, otherwise rows can repeat or vanish
        # between pages.
        entity = query.column_descriptions[0]["entity"]
        query = query.order_by(entity.id)

    return query.offset(page.offset).limit(page.limit).all()


def paginate_list(items: list, page: PageParams, response: Response) -> list:
    """Page a list that was already built in Python."""

    response.headers[TOTAL_COUNT_HEADER] = str(len(items))

    return items[page.offset : page.offset + page.limit]