import pytest
from django.urls import reverse

from post.models import Post


@pytest.mark.django_db
def test_create_post(post_data, user, logged_in_client):
    response = logged_in_client.post(reverse("posts-list"), data=post_data)
    assert response.status_code == 201
    assert Post.objects.count() == 1
    assert Post.objects.first().author == user


@pytest.mark.django_db
def test_create_post_invalid_data(post_data, logged_in_client):
    response = logged_in_client.post(reverse("posts-list"), data={"caption": post_data['caption']})
    assert response.status_code == 400
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_create_post_unauthenticated(post_data, client):
    response = client.post(reverse("posts-list"), data=post_data)
    assert response.status_code == 401
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_update_post(created_post, logged_in_client):
    updated_data = {
        "caption": "this is an updated post content.",
    }
    response = logged_in_client.put(reverse("posts-detail", kwargs={"pk": created_post.pk}), data=updated_data)
    assert response.status_code == 200
    created_post.refresh_from_db()
    assert created_post.caption == updated_data["caption"]


@pytest.mark.django_db
def test_update_post_invalid_data(created_post, logged_in_client):
    updated_data = {"caption": ""}
    response = logged_in_client.put(reverse("posts-detail", kwargs={"pk": created_post.pk}), data=updated_data)
    assert response.status_code == 400
    created_post.refresh_from_db()
    assert created_post.caption != updated_data["caption"]


@pytest.mark.django_db
def test_update_post_unauthenticated(created_post, client):
    updated_data = {
        "caption": "this is an updated post content.",
    }
    response = client.put(reverse("posts-detail", kwargs={"pk": created_post.pk}), data=updated_data)
    assert response.status_code == 401
    created_post.refresh_from_db()
    assert created_post.caption != updated_data["caption"]


@pytest.mark.django_db
def test_delete_post(created_post, logged_in_client):
    response = logged_in_client.delete(reverse("posts-detail", kwargs={"pk": created_post.pk}))
    assert response.status_code == 204
    assert Post.objects.first().is_deleted is True


@pytest.mark.django_db
def test_get_posts(logged_in_client, created_post):
    response = logged_in_client.get(reverse("posts-list"))
    assert response.status_code == 200
    assert response.data['results'].count() == 1
