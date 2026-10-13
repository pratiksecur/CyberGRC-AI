"""List endpoints are bounded and report the total in X-Total-Count."""

import pytest

LIST_ENDPOINTS = [
    "/api/v1/risks/",
    "/api/v1/controls/",
    "/api/v1/audits/",
    "/api/v1/evidence/",
    "/api/v1/audit-findings/",
    "/api/v1/corrective-actions/",
    "/api/v1/risk-treatments/",
]


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
def test_list_still_returns_a_plain_list_with_total(
    client, auth_headers, users, resource_data, url
):
    response = client.get(url, headers=auth_headers(users["admin"]))

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)

    total = int(response.headers["x-total-count"])
    assert total >= len(body)


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
def test_limit_and_offset_page_through_the_results(
    client, auth_headers, users, resource_data, url
):
    headers = auth_headers(users["admin"])

    everything = client.get(url, headers=headers)
    total = int(everything.headers["x-total-count"])

    first = client.get(url, headers=headers, params={"limit": 1})
    assert first.status_code == 200
    assert len(first.json()) <= 1
    assert int(first.headers["x-total-count"]) == total

    beyond = client.get(url, headers=headers, params={"offset": total + 10})
    assert beyond.status_code == 200
    assert beyond.json() == []
    assert int(beyond.headers["x-total-count"]) == total

    if total >= 2:
        second = client.get(
            url, headers=headers, params={"limit": 1, "offset": 1}
        )
        assert first.json()[0]["id"] != second.json()[0]["id"]


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 1001},
        {"limit": -5},
        {"offset": -1},
        {"limit": "abc"},
    ],
)
def test_invalid_paging_values_are_rejected(
    client, auth_headers, users, resource_data, params
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["admin"]),
        params=params,
    )

    assert response.status_code == 422


def test_total_count_header_is_readable_by_the_browser():
    from app.main import app

    cors = next(
        m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"
    )

    assert "X-Total-Count" in cors.kwargs["expose_headers"]