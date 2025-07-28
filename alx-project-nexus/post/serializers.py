from rest_framework import serializers

from post.models import Post, Hashtag
from utils.hashtags import extract_hashtags


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    This serializer is used to represent post data in the API.
    It includes fields such as caption, image, author, created_at, and updated_at.
    The create method is overridden to handle post creation, including extracting hashtags from the caption.
    The update method is overridden to handle post updates, including updating the image and hashtags.
    The delete method is overridden to mark a post as deleted instead of actually deleting it.
    """
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'image', 'author', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

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

        instance.caption = validated_data.get('caption', instance.caption)
        if image:
            instance.image = image

        instance.save()

        caption = validated_data.get('caption')
        hashtags = extract_hashtags(caption)
        instance.hashtags.clear()
        for tag_name in hashtags:
            tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            instance.hashtags.add(tag)

        return instance

    def delete(self, instance, validated_data):
        instance.is_deleted = True
        instance.save()
        return instance
