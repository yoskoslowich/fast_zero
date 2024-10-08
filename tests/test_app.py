from http import HTTPStatus
from fast_zero.schemas import UserPublic
from fastapi.testclient import TestClient


def test_read_root_must_return_ok(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello, World!"}


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "test",
            "email": "test@mail.com",
            "password": "test",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "test",
        "email": "test@mail.com",
    }


def test_read_users(client: TestClient, token, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_not_found(client):
    response = client.get("/users/2")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user(client, user, token):
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test2",
            "email": "test@mail.com",
            "password": "test",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "test2",
        "email": "test@mail.com",
    }


def test_update_user_not_found(client, token):
    response = client.put(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test2",
            "email": "test@mail.com",
            "password": "test",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user(client, token):
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_not_found(client, token):
    response = client.delete(
        "/users/2", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "detail": "User can only delete their own account"
    }


def test_token(client, user):
    response = client.post(
        "/token/",
        data={
            "username": user.username,
            "password": user.clean_password,
        },
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert token["token_type"] == "Bearer"
