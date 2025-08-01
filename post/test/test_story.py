import pytest
from django.urls import reverse

from post.models import Story


@pytest.mark.django_db
def test_create_story(story_data, user, logged_in_client):
    response = logged_in_client.post(reverse("stories-list"), data=story_data)
    assert response.status_code == 201
    assert Story.objects.count() == 1
    assert Story.objects.first().author == user


@pytest.mark.django_db
def test_create_story_invalid_data(story_data, logged_in_client):
    response = logged_in_client.post(reverse("stories-list"), data={"caption": story_data['caption']})
    assert response.status_code == 400
    assert Story.objects.count() == 0


@pytest.mark.django_db
def test_create_story_unauthenticated(story_data, client):
    response = client.post(reverse("stories-list"), data=story_data)
    assert response.status_code == 401
    assert Story.objects.count() == 0


@pytest.mark.django_db
def test_update_story(created_story, logged_in_client):
    updated_data = {
        "caption": "this is an updated story content.",
    }
    response = logged_in_client.put(reverse("stories-detail", kwargs={"pk": created_story.pk}), data=updated_data)
    assert response.status_code == 200
    created_story.refresh_from_db()
    assert created_story.caption == updated_data["caption"]


@pytest.mark.django_db
def test_update_story_invalid_data(created_story, logged_in_client):
    updated_data = {"caption": ""}
    response = logged_in_client.put(reverse("stories-detail", kwargs={"pk": created_story.pk}), data=updated_data)
    assert response.status_code == 400
    created_story.refresh_from_db()
    assert created_story.caption != updated_data["caption"]


@pytest.mark.django_db
def test_update_story_unauthenticated(created_story, client):
    updated_data = {
        "caption": "this is an updated story content.",
    }
    response = client.put(reverse("stories-detail", kwargs={"pk": created_story.pk}), data=updated_data)
    assert response.status_code == 401
    created_story.refresh_from_db()
    assert created_story.caption != updated_data["caption"]


@pytest.mark.django_db
def test_delete_story(created_story, logged_in_client):
    response = logged_in_client.delete(reverse("stories-detail", kwargs={"pk": created_story.pk}))
    assert response.status_code == 204
    assert Story.objects.first().is_deleted is True


@pytest.mark.django_db
def test_get_story(logged_in_client, created_story):
    response = logged_in_client.get(reverse("stories-list"))
    assert response.status_code == 200
    assert len(response.data['results']) == 1
