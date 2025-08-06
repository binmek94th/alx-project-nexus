import pytest
from django.urls import reverse

from post.models import Post, StoryLike


@pytest.mark.django_db
def test_create_like(created_story, user, logged_in_client):
    url = reverse("story_like-list") + "?type=story"
    response = logged_in_client.post(url, data={"story": created_story.id})
    assert response.status_code == 201
    assert StoryLike.objects.count() == 1
    assert StoryLike.objects.first().user == user


@pytest.mark.django_db
def test_create_like_invalid_data(post_data, user, logged_in_client):
    url = reverse("story_like-list") + "?type=story"
    response = logged_in_client.post(url, data={"story": "3242k34234234"})
    assert response.status_code == 400
    assert StoryLike.objects.count() == 0


@pytest.mark.django_db
def test_create_like_unauthenticated(created_story, client):
    url = reverse("story_like-list") + "?type=story"
    response = client.post(url, data={"story": created_story.id})
    assert response.status_code == 401
    assert StoryLike.objects.count() == 0


@pytest.mark.django_db
def test_delete_like(created_story_like, logged_in_client):
    url = reverse("story_like-detail", kwargs={"pk": created_story_like.pk}) + "?type=story"
    response = logged_in_client.delete(url)
    assert response.status_code == 204
    assert StoryLike.objects.all().count() == 0
