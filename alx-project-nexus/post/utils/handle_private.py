from typing import Type, Union, Optional

from post.models import Post, Comment, Like
from user.models import Follow


def handle_private_posts(user, model: Type[Union[Like, Comment]],  post_id: Optional[str] = None):
    """
    Handles the retrieval of posts, likes, or comments based on the user's privacy settings and relationships.
    This function checks if the post is public, if the user is the author, or if the user is following the author.
    If the post is private and the user is not following the author, it returns an empty queryset.
    If the post_id is provided, it retrieves the specific post and checks the privacy settings.
    If the post is public or the user is the author or following the author, it returns the relevant model objects.
    :param user:
    :param model:
    :param post_id:
    :return:
    """
    if post_id:
        try:
            post = Post.objects.select_related('author').get(id=post_id)
        except Post.DoesNotExist:
            return model.objects.none()

        is_following = Follow.objects.select_related('post').filter(follower=user, following=post.author).exists()

        if post.author.privacy_choice == "public" or post.author == user or is_following:
            return model.objects.filter(post_id=post_id)
        else:
            return model.objects.none()
    return model.objects.filter(user=user)
