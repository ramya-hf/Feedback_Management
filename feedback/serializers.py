from rest_framework import serializers
from .models import Board, Feedback, Comment
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

class FeedbackSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author_name', read_only=True)
    author_email = serializers.CharField(source='author_email', read_only=True)
    vote_count = serializers.IntegerField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    upvotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    downvotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    file = serializers.FileField(required=False, allow_null=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Feedback
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'category', 'board',
            'author', 'author_name', 'author_email', 'assigned_to', 'upvotes', 'downvotes',
            'vote_count', 'total_votes', 'comment_count', 'created_at', 'updated_at', 'is_active',
            'anonymous_email', 'anonymous_name', 'file', 'tags'
        ]
        read_only_fields = ['id', 'author', 'author_name', 'author_email', 'vote_count', 'total_votes', 'comment_count', 'created_at', 'updated_at']

class FeedbackVoteSerializer(serializers.Serializer):
    vote_type = serializers.ChoiceField(choices=['upvote', 'downvote'])

class FeedbackStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Feedback.Status.choices)

class FeedbackTagSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField())

class FeedbackFileSerializer(serializers.Serializer):
    file = serializers.FileField()

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author_name', read_only=True)
    author_email = serializers.CharField(source='author_email', read_only=True)
    vote_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    is_reply = serializers.BooleanField(source='is_reply', read_only=True)
    upvotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    downvotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'feedback', 'author', 'author_name', 'author_email', 'parent',
            'is_reply', 'reply_count', 'upvotes', 'downvotes', 'vote_count',
            'created_at', 'updated_at', 'is_active', 'anonymous_email', 'anonymous_name'
        ]
        read_only_fields = ['id', 'author', 'author_name', 'author_email', 'is_reply', 'reply_count', 'upvotes', 'downvotes', 'vote_count', 'created_at', 'updated_at']

class CommentVoteSerializer(serializers.Serializer):
    vote_type = serializers.ChoiceField(choices=['upvote', 'downvote'])

class CommentModerationSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()
