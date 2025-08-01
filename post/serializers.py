from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from post.models import Post, Hashtag, Like, Comment, Story, StoryLike
from post.utils.check_toxicity import is_flagged
from post.utils.hashtags import extract_hashtags
from user.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    This serializer is used to represent post data in the API.
    It includes fields such as caption, image, author, created_at, and updated_at.
    The create method is overridden to handle post creation, including extracting hashtags from the caption.
    The update method is overridden to handle post updates, including updating the image and hashtags.
    """
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'image', 'author', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def validate_caption(self, value):
        if is_flagged(value):
            raise serializers.ValidationError("Caption contains toxic content.")
        return value.lower()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        image = request.FILES.get('image') if request else None
        if not image:
            raise serializers.ValidationError("Image is required for creating a post.")

        hashtags = extract_hashtags(validated_data['caption'])
        post = Post.objects.create(**validated_data, author=user)

        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            post.hashtags.add(tag)

        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        image = request.FILES.get('image') if request else None
        caption = validated_data.get('caption')

        if caption:
            instance.caption = caption

        if image:
            instance.image = image

        instance.save()

        hashtags = extract_hashtags(caption)
        instance.hashtags.clear()
        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            instance.hashtags.add(tag)

        return instance


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing posts.
    This serializer is used to represent posts in a list format.
    It includes fields such as id, caption, image, author, created_at, and updated_at.
    The author field is a nested serializer that represents the user who created the post.
    The read_only_fields are set to ensure that certain fields cannot be modified
    when creating or updating a post.
    """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'image', 'author', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')


class StorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Story model.
    This serializer is used to represent story data in the API.
    It includes fields such as caption, image, author, created_at, and expires_at.
    The create method is overridden to handle story creation, including extracting hashtags from the caption
    and setting an expiration time for the story.
    The update method is overridden to handle story updates, including updating the image and hashtags.
    """
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Story
        fields = ('id', 'caption', 'image', 'author', 'created_at', 'expires_at')
        read_only_fields = ('id', 'author', 'created_at', 'expires_at')

    def validate_caption(self, value):
        if is_flagged(value):
            raise serializers.ValidationError("Caption contains toxic content.")
        return value.lower()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        image = request.FILES.get('image') if request else None
        if not image:
            raise serializers.ValidationError("Image is required for creating a story.")

        hashtags = extract_hashtags(validated_data['caption'])
        expires_at = timezone.now() + timedelta(hours=24)
        story = Story.objects.create(**validated_data, author=user, expires_at=expires_at)

        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            story.hashtags.add(tag)

        return story

    def update(self, instance, validated_data):
        request = self.context.get('request')
        image = request.FILES.get('image') if request else None
        caption = validated_data.get('caption')

        if caption:
            instance.caption = caption

        if image:
            instance.image = image

        instance.save()

        hashtags = extract_hashtags(caption)
        instance.hashtags.clear()
        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            instance.hashtags.add(tag)

        return instance


class StoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing stories.
    This serializer is used to represent stories in a list format.
    It includes fields such as id, caption, image, author, created_at, and expires at.
    The author field is a nested serializer that represents the user who created the story.
    The read_only_fields are set to ensure that certain fields cannot be modified
    when creating or updating a story.
    """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Story
        fields = ('id', 'caption', 'author', 'created_at', 'expires_at')
        read_only_fields = ('id', 'author', 'created_at', 'expires_at')


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.
    This serializer is used to represent likes on posts.
    It includes fields such as post and user.
    The create method is overridden to handle the creation of likes.
    """

    class Meta:
        model = Like
        fields = ('id', 'post', 'created_at')
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        post = validated_data.get('post')
        user = self.context['user']
        if Like.objects.filter(post=post, user=user).exists():
            raise serializers.ValidationError("You already liked this post.")

        return Like.objects.create(post=post, user=user)


class StoryLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.
    This serializer is used to represent likes on stories.
    It includes fields such as story and user.
    The create method is overridden to handle the creation of likes.
    """

    class Meta:
        model = StoryLike
        fields = ('id', 'story', 'created_at')
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        story = validated_data.get('story')
        user = self.context['user']
        if StoryLike.objects.filter(story=story, user=user).exists():
            raise serializers.ValidationError("You already liked this story.")

        return StoryLike.objects.create(story=story, user=user)


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    This serializer is used to represent comments on posts.
    It includes fields such as post and user.
    The create method is overridden to handle the creation of comments.
    """

    class Meta:
        model = Comment
        fields = ('id', 'post', 'created_at', 'comment', 'content')
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['user']

        return Comment.objects.create(**validated_data, user=user)


class CommentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing comments with nested replies.
    This serializer is used to represent comments in a tree structure.
    It includes fields such as id, post, created_at, content, and comment.
    The children field is a SerializerMethodField that retrieves nested comments.
    The get_children method uses the CommentListSerializer to serialize child comments.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'created_at', 'content', 'comment', 'children')
        read_only_fields = ['id', 'created_at']

    def get_children(self, obj):
        return CommentListSerializer(getattr(obj, "_children", []), many=True, context=self.context).data
