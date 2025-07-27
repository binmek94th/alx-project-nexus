from rest_framework import serializers

from user.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'email_verified',
                  'password', 'is_active', 'is_staff')
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
        fields = ('id', 'username', 'email', 'full_name', 'email_verified')
        read_only_fields = ('id', 'email_verified')

    def update(self, instance, validated_data):
        user = self.context['user']
        if user.is_authenticated and (not user.is_superuser or not user.is_staff):
            if 'role' in validated_data and validated_data['role'] not in ['viewer', 'talent']:
                raise serializers.ValidationError(
                    "You do not have permission to assign this role. Only 'viewer' or 'talent' roles are allowed.")
        for attr in ['username', 'first_name', 'last_name', 'role']:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()
        return instance


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


class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Following model.
    This serializer is used to handle the creation and representation of following relationships.
    """
    class Meta:
        model = Follow
        fields = ['following']

    def create(self, validated_data):
        user = self.context['user']
        following_user = validated_data['following']

        if user == following_user:
            raise serializers.ValidationError("You cannot follow yourself.")

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
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'following', 'created_at']
        read_only_fields = ['created_at']


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
