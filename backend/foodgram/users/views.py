from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, CustomUser
from .serializers import CustomUserSerializer, FollowSerializer

User = CustomUser


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        check_subscription = Follow.objects.filter(user=user, author=author).exists()
        if request.method == 'POST':
            if check_subscription or user == author:
                return Response(
                    'Вы уже подписаны на этого пользователя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribe = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                subscribe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if check_subscription:
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)
