import uuid
from mptt.models import MPTTModel, TreeForeignKey

from django.db import models


class Hashtag(models.Model):
    """
    Represents a hashtag that can be associated with posts.
    Each hashtag has a unique name.
    The name is stored as a CharField with a maximum length of 100 characters.
    The __str__ method returns the hashtag name prefixed with a hash symbol.
    This model is used to categorize posts and allow users to search for content related to specific topics
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    """
    Represents a post created by a user.
    Each post has a unique identifier, a caption, an author (user), an image,
    and a many-to-many relationship with hashtags.
    The created_at and updated_at fields track when the post was created and last updated.
    The is_deleted field is used to mark a post as deleted without actually removing it from the
    database.
    The __str__ method returns the caption of the post.
    The Meta class specifies the ordering of posts by creation date in descending order
    and sets a verbose name for the model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caption = models.TextField()
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='image/posts')
    hashtags = models.ManyToManyField(Hashtag, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'


class Story(models.Model):
    """
    Represents a story created by a user.
    Each story has a unique identifier, a caption, an image, an author (user),
    and an expiration date.
    The created_at field tracks when the story was created.
    The Meta class specifies the ordering of stories by creation date in descending order
    and sets a verbose name for the model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caption = models.TextField()
    image = models.ImageField(upload_to='image/stories/')
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='stories')
    hashtags = models.ManyToManyField(Hashtag, related_name='story')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Story'


class TypeChoice(models.TextChoices):
    POST = 'post', 'Post'
    STORY = 'story', 'Story'


class Like(models.Model):
    """
    Represents a like on a post by a user.
    Each like has a unique identifier, a reference to the post it belongs to,
    a reference to the user who liked the post, and a timestamp for when the like was
    created.
    The unique_together constraint ensures that a user can only like a post once.
    The Meta class specifies the ordering of likes by creation date in descending order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TypeChoice.choices, default=TypeChoice.POST)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']


class Comment(models.Model):
    """
    Represents a comment on a post by a user.
    Each comment has a unique identifier, a reference to the post it belongs to,
    a reference to the user who made the comment, the content of the comment,
    and timestamps for when the comment was created and last updated.
    The Meta class specifies the ordering of comments by creation date in descending order
    and sets a verbose name for the model.
    nested comments (replies) are supported through a self-referential foreign key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='comments')
    comment = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=10, choices=TypeChoice.choices, default=TypeChoice.POST)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
