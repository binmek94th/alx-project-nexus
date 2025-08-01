import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_notification(logged_in_client):
    response = logged_in_client.get(reverse("notifications-list"))
    assert response.status_code == 200
