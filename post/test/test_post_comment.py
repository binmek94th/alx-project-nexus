import pytest
from django.urls import reverse

from post.models import Comment


@pytest.mark.django_db
def test_create_comment(created_post, user, logged_in_client):
    url = reverse("comment-list")
    response = logged_in_client.post(url, data={"post": created_post.id, "content": "This is a test comment."})
    print(response.content)
    assert response.status_code == 201
    assert Comment.objects.count() == 1
    assert Comment.objects.first().user == user


@pytest.mark.django_db
def test_create_nested_comment(created_post, user, logged_in_client, created_comment):
    url = reverse("comment-list")
    response = logged_in_client.post(url, data={"post": created_post.id, "content": "This is a test comment.",
                                                "comment": created_comment.id})
    assert response.status_code == 201
    assert Comment.objects.count() == 2
    assert Comment.objects.first().user == user
    assert Comment.objects.first().comment == created_comment


@pytest.mark.django_db
def test_create_comment_invalid_data(created_post, user, logged_in_client):
    url = reverse("comment-list")
    response = logged_in_client.post(url, data={"post": created_post.id, "comment": ""})
    assert response.status_code == 400
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_create_comment_unauthenticated(created_post, client):
    url = reverse("comment-list")
    response = client.post(url, data={"post": created_post.id})
    assert response.status_code == 401
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_delete_comment(created_comment, logged_in_client):
    url = reverse("comment-detail", kwargs={"pk": created_comment.pk})
    with pytest.raises(NotImplementedError):
        logged_in_client.delete(url)
    assert Comment.objects.all().count() == 1
