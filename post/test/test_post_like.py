import pytest
from django.urls import reverse

from post.models import Post, Like


@pytest.mark.django_db
def test_create_like(created_post, user, logged_in_client):
    url = reverse("like-list") + "?type=post"
    response = logged_in_client.post(url, data={"post": created_post.id})
    assert response.status_code == 201
    assert Like.objects.count() == 1
    assert Like.objects.first().user == user


@pytest.mark.django_db
def test_create_like_invalid_data(post_data, user, logged_in_client):
    url = reverse("like-list") + "?type=post"
    response = logged_in_client.post(url, data={"post": "3242k34234234"})
    assert response.status_code == 400
    assert Like.objects.count() == 0


@pytest.mark.django_db
def test_create_like_unauthenticated(created_post, client):
    url = reverse("like-list") + "?type=post"
    response = client.post(url, data={"post": created_post.id})
    assert response.status_code == 401
    assert Like.objects.count() == 0


@pytest.mark.django_db
def test_delete_like(created_like, logged_in_client):
    url = reverse("like-detail", kwargs={"pk": created_like.pk}) + "?type=post"
    response = logged_in_client.delete(url)
    assert response.status_code == 204
    assert Like.objects.all().count() == 0
