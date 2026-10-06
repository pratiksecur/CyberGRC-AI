def test_regulatory_intelligence_endpoint_returns_200(
    client,
    users,
    auth_headers,
):

    response = client.get(
        "/api/v1/frameworks/intelligence",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert "framework_count" in body
    assert "total_requirements" in body
    assert "overall_posture" in body
    assert "frameworks" in body


def test_regulatory_intelligence_endpoint_supports_manager(
    client,
    users,
    auth_headers,
):

    response = client.get(
        "/api/v1/frameworks/intelligence",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200


def test_regulatory_intelligence_endpoint_supports_auditor(
    client,
    users,
    auth_headers,
):

    response = client.get(
        "/api/v1/frameworks/intelligence",
        headers=auth_headers(
            users["auditor"]
        ),
    )

    assert response.status_code == 200


def test_regulatory_intelligence_requires_auth(
    client,
):

    response = client.get(
        "/api/v1/frameworks/intelligence"
    )

    assert response.status_code == 401