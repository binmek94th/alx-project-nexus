import pytest
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from post.models import Post
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
def image():
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B',
        content_type='image/jpeg'
    )


@pytest.fixture()
def post_data(image, user):
    return {
        "caption": "This is a test post content.",
        "author": User.objects.first(),
        "image": image
    }


@pytest.fixture()
def story_data(image, user):
    return {
        "caption": "This is a test story content.",
        "author": User.objects.first(),
        "image": image
    }


@pytest.fixture()
def created_like(post_data, user):
    from post.models import Post, Like
    return Like.objects.create(
        post=Post.objects.create(**post_data),
        user=user
    )


@pytest.fixture()
def created_story_like(story_data, user):
    from post.models import Story, StoryLike
    return StoryLike.objects.create(
        story=Story.objects.create(**story_data, expires_at=timezone.now() + timedelta(days=1)),
        user=user,
    )


@pytest.fixture()
def created_comment(post_data, user):
    from post.models import Comment
    return Comment.objects.create(
        post=Post.objects.create(**post_data),
        content="This is a test comment.",
        user=user
    )


@pytest.fixture()
def created_post(post_data):
    from post.models import Post
    return Post.objects.create(**post_data)


@pytest.fixture()
def created_story(story_data):
    from post.models import Story
    return Story.objects.create(**story_data, expires_at=timezone.now() + timedelta(days=1))


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
