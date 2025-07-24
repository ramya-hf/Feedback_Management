from rest_framework import serializers
from .models import Board
from accounts.models import User

class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderators = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    feedback_count = serializers.IntegerField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'description', 'slug', 'visibility',
            'allow_anonymous_feedback', 'require_approval', 'allow_comments', 'allow_voting',
            'owner', 'moderators', 'members', 'created_at', 'updated_at', 'is_active',
            'feedback_count', 'total_votes'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'feedback_count', 'total_votes']

class BoardMemberSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

class BoardModeratorSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
