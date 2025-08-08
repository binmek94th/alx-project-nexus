from rest_framework import serializers

from user.models import Follow, User, FollowRequest
from post.utils.exception import FollowRequestSent


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    This serializer is used to represent user data in the API.
    It includes fields such as username, email, full name, email verification status,
    password, and privacy choice.
    The password field is set to write-only to ensure it is not exposed in the serialized output
    The create method is overridden to handle user creation, setting the password and initial active status.
    The read-only fields include id, is_active, is_staff, and email_verified.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'email_verified',
                  'password', 'is_active', 'is_staff', 'privacy_choice', 'bio', 'profile_picture')
        read_only_fields = ('id', 'is_active', 'is_staff', 'email_verified')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'bio', 'profile_picture', 'privacy_choice')
        read_only_fields = ('id', 'email_verified')


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'password')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        new_email = validated_data.get('email')
        if new_email and new_email != instance.email:
            instance.email_verified = False
            instance.email = new_email
            instance.save()
            return instance
        raise ValueError("This account already using this email.")


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer for a simple representation of a user.
    This serializer is used to represent basic user information such as id, username, and profile picture.
    It is used in nested serializers where only basic user information is needed.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_picture')


class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Following model.
    This serializer is used to handle the creation and representation of following relationships.
    if the user is trying to follow a private account, it will create a follow request instead.
    If the user is trying to follow themselves, it will raise a validation error.
    If the user is already following the account, it will raise a validation error.
    """
    class Meta:
        model = Follow
        fields = ['following']

    def create(self, validated_data):
        user = self.context['user']
        following_user = validated_data['following']
        following_user_obj = User.objects.filter(id=following_user.id).first()

        if user == following_user:
            raise serializers.ValidationError("You cannot follow yourself.")

        if following_user_obj.privacy_choice == 'private':
            request_exists = FollowRequest.objects.filter(sender=user, receiver=following_user).exists()
            if request_exists:
                raise serializers.ValidationError("Follow request already sent.")
            FollowRequest.objects.create(sender=user, receiver=following_user)
            raise FollowRequestSent()

        follow, created = Follow.objects.get_or_create(
            follower=user,
            following=following_user
        )
        if not created:
            raise serializers.ValidationError("You are already following this user.")

        return follow


class FollowingListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing followers and following users.
    This serializer is used to represent the list of users that a user is following or who are following them.
    """
    following = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'following', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        following_data = rep.pop("following", {})
        return {**rep, "user_id": following_data['id'], "id": rep['id'], **following_data}


class FollowerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing followers and following users.
    This serializer is used to represent the list of users that a user is following or who are following them.
    """
    follower = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        follower_data = rep.pop("follower", {})
        return {**rep, "user_id": follower_data['id'], "id": rep['id'], **follower_data}


class FollowRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for handling follow requests.
    This serializer is used to represent follow requests sent by users to other users.
    It includes the sender and receiver of the follow request.
    It also allows updating the follow request to approve or reject it.
    If the follow request is approved, it creates a follow relationship.
    If the follow request is rejected, it simply updates the request without creating a follow relationship.
    The create method is overridden to prevent direct creation of follow requests through this serializer.
    """
    sender = UserSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ['id', 'sender', 'created_at', 'is_approved', 'is_rejected']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        raise serializers.ValidationError("Follow requests cannot be created directly. Use the FollowingSerializer "
                                          "instead.")

    def update(self, instance, validated_data):
        is_approved = validated_data.get('is_approved')
        is_rejected = validated_data.get('is_rejected', False)
        if is_rejected:
            instance.is_rejected = True
            instance.save()
            return instance

        if is_approved is not None:
            instance.is_approved = is_approved
            instance.save()
            if is_approved:
                Follow.objects.get_or_create(
                    follower=instance.sender,
                    following=instance.receiver
                )
            return instance
        raise serializers.ValidationError("Is approved or is rejected field is required for update.")
