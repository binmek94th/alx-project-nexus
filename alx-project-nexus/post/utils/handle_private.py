from typing import Type, Union
from django.db.models import QuerySet
from post.models import Like, Comment, Post, Story, StoryLike
from user.models import Follow


def check_owner(author, user):
    """
    Check if the author is the same as the user.
    This function checks if the author of a post or story is the same as the user
    :param author:
    :param user:
    :return:
    """
    if author == user:
        return True
    return False


def check_private(author, user):
    """
    Check if the author's privacy setting is private and the user is not the author.
    This function checks if the author's privacy choice is set to private and the user
    :param author:
    :param user:
    :return:
    """
    if author.privacy_choice == "private" and author != user:
        return True
    return False


def check_private_allowed(user, author_id):
    """
    Check if the user is allowed to view the author's private content.
    This function checks if the user is following the author.
    :param user:
    :param author_id:
    :return:
    """
    return Follow.objects.filter(follower=user, following=author_id).exists()


def generate_like_queryset(content_model_type: Type[Union[Post, Story]], content_id, user) -> QuerySet:
    """
    Generate a queryset for likes based on the content model type and content ID.
    This function retrieves likes for a specific post or story based on the content model type
    and content ID. It checks if the user is the owner of the content or if the content is private.
    If the content is private, it checks if the user is allowed to view it based on their follow status.
    If the content ID is provided, it filters likes for that specific content.
    If no content ID is provided, it retrieves likes for the user.
    :param content_model_type:
    :param content_id:
    :param user:
    :return:
    """
    content_model = Post if content_model_type == 'post' else Story
    if content_model == Post:
        model = Like
        fk_field = 'post'
    else:
        model = StoryLike
        fk_field = 'story'

    if content_id:
        content = content_model.objects.select_related('author').get(id=content_id)
        if check_owner(content.author, user):
            return model.objects.filter(**{fk_field: content_id})

        if check_private(content.author, user):
            if not check_private_allowed(user, content.author.id):
                return model.objects.none()

        return model.objects.filter(**{fk_field: content_id})
    return model.objects.filter(user=user)


def generate_comment_queryset(post_id, user) -> QuerySet:
    """
    Generate a queryset for comments based on the post ID and user.
    This function retrieves comments for a specific post based on the post ID.
    It checks if the user is the owner of the post or if the post is private.
    If the post is private, it checks if the user is allowed to view it based on their follow status.
    If the post ID is provided, it filters comments for that specific post.
    :param post_id:
    :param user:
    :return:
    """
    if post_id:
        post = Post.objects.select_related('author').get(id=post_id)
        if check_owner(post.author, user):
            return Comment.objects.filter(post=post_id)

        content = Comment.objects.select_related('user').get(id=post_id)
        if check_private(content.user, user):
            if not check_private_allowed(user, content.user.id):
                return Comment.objects.none()

        return Comment.objects.select_related('user', 'comment').filter(post=post_id)
    return Comment.objects.filter(user=user)
