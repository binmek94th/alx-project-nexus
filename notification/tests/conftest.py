import pytest
from rest_framework.test import APIClient

from user.models import User


@pytest.fixture()
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpassword',
        full_name='Test User',
        bio='This is a test user.',
        is_active=True,
        email_verified=True,
        email="test@gmail.com")


@pytest.fixture
def logged_in_client(user):
    client = APIClient()
    response = client.post('/api/token/', {
        "username": user.username,
        "password": "testpassword"
    })
    assert response.status_code == 200, f"Token auth failed: {response.content}"
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
