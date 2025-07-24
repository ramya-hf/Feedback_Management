from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Board
from .serializers import BoardSerializer, BoardMemberSerializer, BoardModeratorSerializer
from accounts.models import User

# Create your views here.

class IsBoardOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.can_moderate(request.user)

class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.can_edit(request.user)

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visibility', 'is_active', 'owner']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsBoardOwner()]
        elif self.action in ['add_member', 'remove_member', 'add_moderator', 'remove_moderator']:
            return [IsBoardOwnerOrModerator()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        board = self.get_object()
        serializer = BoardMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(pk=serializer.validated_data['user_id'])
        board.members.add(user)
        return Response({'detail': 'Member added.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        board = self.get_object()
        serializer = BoardMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(pk=serializer.validated_data['user_id'])
        board.members.remove(user)
        return Response({'detail': 'Member removed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-moderator')
    def add_moderator(self, request, pk=None):
        board = self.get_object()
        serializer = BoardModeratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(pk=serializer.validated_data['user_id'])
        board.moderators.add(user)
        return Response({'detail': 'Moderator added.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-moderator')
    def remove_moderator(self, request, pk=None):
        board = self.get_object()
        serializer = BoardModeratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(pk=serializer.validated_data['user_id'])
        board.moderators.remove(user)
        return Response({'detail': 'Moderator removed.'}, status=status.HTTP_200_OK)
