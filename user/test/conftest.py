import pytest
from user.models import User
from rest_framework.test import APIClient


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def setup_users():
    return {
        "username": "test_user",
        "email": "test@gmail.com",
        "password": "test_password",
        "full_name": "Test User",
    }


@pytest.fixture()
def setup_user_admin():
    return {
        "username": "admin",
        "email": "admin1@gmail.com",
        "password": "test_password",
        "full_name": "Test User",
        "is_superuser": True,
        "is_staff": True,
    }


@pytest.fixture()
def created_user(setup_users):
    setup_users["username"] = "test_user1"
    setup_users["email"] = "test_user@gmail.com"
    user = User.objects.create(**setup_users)
    user.set_password(setup_users['password'])
    user.save()
    return user


@pytest.fixture()
def admin_created_user(setup_user_admin):
    user = User.objects.create(**setup_user_admin)
    user.set_password(setup_user_admin['password'])
    user.save()
    return user


@pytest.fixture()
def active_created_user(setup_users):
    user = User.objects.create(**setup_users, is_active=True)
    user.set_password(setup_users['password'])
    user.save()
    return user


@pytest.fixture()
def login_user(active_created_user, setup_users):
    return {
        "username": "test_user",
        "password": "test_password"
    }


@pytest.fixture()
def admin_login_user(active_created_user, setup_users):
    return {
        "username": "admin",
        "password": "test_password"
    }


@pytest.fixture()
def logged_in_client(active_created_user, login_user, client):
    response = client.post('/api/token/', login_user)
    token = response.data['access']
    return token


@pytest.fixture()
def logged_in_admin_client(admin_created_user, admin_login_user, client):
    response = client.post('/api/token/', admin_login_user)
    token = response.data['access']
    return token
