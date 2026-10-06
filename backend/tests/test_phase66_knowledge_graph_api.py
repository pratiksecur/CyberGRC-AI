def test_admin_can_access_knowledge_graph(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/knowledge-graph",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert "nodes" in body
    assert "edges" in body
    assert "summary" in body
    assert "generated_at" in body


def test_manager_can_access_knowledge_graph(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/knowledge-graph",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200


def test_employee_can_access_visible_knowledge_graph(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/knowledge-graph",
        headers=auth_headers(
            users["employee"]
        ),
    )

    assert response.status_code == 200


def test_unauthenticated_cannot_access_knowledge_graph(
    client,
):
    response = client.get(
        "/api/v1/intelligence/knowledge-graph"
    )

    assert response.status_code == 401


def test_focus_risk_endpoint(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = resource_data[
        "risks"
    ]["admin"]

    response = client.get(
        (
            "/api/v1/intelligence/"
            f"knowledge-graph?risk_id={risk.id}"
        ),
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["focus_risk_id"]
        == risk.id
    )


def test_manager_cannot_focus_admin_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = resource_data[
        "risks"
    ]["admin"]

    response = client.get(
        (
            "/api/v1/intelligence/"
            f"knowledge-graph?risk_id={risk.id}"
        ),
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 404