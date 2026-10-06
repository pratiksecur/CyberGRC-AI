from unittest.mock import patch


def test_admin_can_use_grc_analyst(
    client,
    users,
    auth_headers,
):
    with patch(
        "app.services.ai_grc_analyst_ai_service.get_ai_provider"
    ) as provider_factory:
        provider = provider_factory.return_value

        provider.generate.return_value = (
            "The most important issue is an unresolved "
            "critical risk.\n\n"
            "- Review the risk treatment.\n"
            "- Validate supporting evidence."
        )

        response = client.post(
            "/api/v1/ai/grc-analyst",
            json={
                "question":
                    "What are our biggest risks?"
            },
            headers=auth_headers(
                users["admin"]
            ),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "RISK"
    assert data["human_decision_required"] is True
    assert data["analysis"]


def test_manager_can_use_grc_analyst(
    client,
    users,
    auth_headers,
):
    with patch(
        "app.services.ai_grc_analyst_ai_service.get_ai_provider"
    ) as provider_factory:
        provider = provider_factory.return_value

        provider.generate.return_value = (
            "Control effectiveness requires review."
        )

        response = client.post(
            "/api/v1/ai/grc-analyst",
            json={
                "question":
                    "Which controls are ineffective?"
            },
            headers=auth_headers(
                users["manager"]
            ),
        )

    assert response.status_code == 200


def test_unauthenticated_cannot_use_grc_analyst(
    client,
):
    response = client.post(
        "/api/v1/ai/grc-analyst",
        json={
            "question":
                "What are our biggest risks?"
        },
    )

    assert response.status_code == 401


def test_invalid_question_is_rejected(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/ai/grc-analyst",
        json={
            "question": "x",
        },
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 422