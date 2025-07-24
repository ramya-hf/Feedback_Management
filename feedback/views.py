from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Feedback, Comment
from .serializers import FeedbackSerializer, FeedbackVoteSerializer, FeedbackStatusSerializer, FeedbackTagSerializer, FeedbackFileSerializer, CommentSerializer, CommentVoteSerializer, CommentModerationSerializer
from accounts.models import User

# Create your views here.

class IsFeedbackOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.can_edit(request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.filter(is_active=True)
    serializer_class = FeedbackSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'board', 'assigned_to']
    search_fields = ['title', 'description', 'anonymous_name', 'anonymous_email']
    ordering_fields = ['created_at', 'updated_at', 'vote_count']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'set_status', 'add_tag', 'remove_tag', 'attach_file']:
            return [IsFeedbackOwnerOrModerator()]
        elif self.action in ['vote', 'remove_vote']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='vote')
    def vote(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data['vote_type']
        success = feedback.add_vote(request.user, vote_type)
        if not success:
            return Response({'detail': 'Voting not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'detail': f'{vote_type.capitalize()} registered.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-vote')
    def remove_vote(self, request, pk=None):
        feedback = self.get_object()
        feedback.remove_vote(request.user)
        return Response({'detail': 'Vote removed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='set-status')
    def set_status(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback.status = serializer.validated_data['status']
        feedback.save()
        return Response({'detail': 'Status updated.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-tag')
    def add_tag(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tags = serializer.validated_data['tags']
        # Assume feedback.tags is a list field or m2m
        feedback.tags = list(set(getattr(feedback, 'tags', []) + tags))
        feedback.save()
        return Response({'detail': 'Tags added.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-tag')
    def remove_tag(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tags = serializer.validated_data['tags']
        feedback.tags = [tag for tag in getattr(feedback, 'tags', []) if tag not in tags]
        feedback.save()
        return Response({'detail': 'Tags removed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attach-file')
    def attach_file(self, request, pk=None):
        feedback = self.get_object()
        serializer = FeedbackFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback.file = serializer.validated_data['file']
        feedback.save()
        return Response({'detail': 'File attached.'}, status=status.HTTP_200_OK)

class IsCommentOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.can_edit(request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['feedback', 'author', 'parent', 'is_active']
    search_fields = ['content', 'anonymous_name', 'anonymous_email']
    ordering_fields = ['created_at', 'updated_at', 'vote_count']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'moderate']:
            return [IsCommentOwnerOrModerator()]
        elif self.action in ['vote', 'remove_vote']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='vote')
    def vote(self, request, pk=None):
        comment = self.get_object()
        serializer = CommentVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data['vote_type']
        if not comment.can_vote(request.user):
            return Response({'detail': 'Voting not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        if vote_type == 'upvote':
            comment.upvotes.add(request.user)
            comment.downvotes.remove(request.user)
        elif vote_type == 'downvote':
            comment.downvotes.add(request.user)
            comment.upvotes.remove(request.user)
        comment.save()
        return Response({'detail': f'{vote_type.capitalize()} registered.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-vote')
    def remove_vote(self, request, pk=None):
        comment = self.get_object()
        comment.upvotes.remove(request.user)
        comment.downvotes.remove(request.user)
        comment.save()
        return Response({'detail': 'Vote removed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='moderate')
    def moderate(self, request, pk=None):
        comment = self.get_object()
        serializer = CommentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment.is_active = serializer.validated_data['is_active']
        comment.save()
        return Response({'detail': 'Comment moderation updated.'}, status=status.HTTP_200_OK)
