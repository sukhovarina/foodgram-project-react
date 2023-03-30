from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, SAFE_METHODS
)
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from .filters import RecipeFilter, IngredientSearchFilter
from .pagination import Pagination
from .permissions import IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateSerializer, FavoriteSerializer, ShoppingCartSerializer
)

FILENAME = 'shoppingcart.txt'


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def get_favorite(self, request, pk=None):
        user = request.user
        queryset = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            favorite = Favorite.objects.create(user=user, recipe=queryset)
            context = {'request': request}
            serializer = FavoriteSerializer(favorite, context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(user=user, recipe=queryset)
        if request.method == 'DELETE':
            if not favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        queryset = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            shopping_cart = ShoppingCart.objects.create(user=user, recipe=queryset)
            context = {'request': request}
            serializer = ShoppingCartSerializer(shopping_cart, context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=queryset)
        if request.method == 'DELETE':
            if not shopping_cart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(total=Sum('amount'))
        result = ''
        for ingredient in ingredients:
            result += ''.join([
                f'{ingredient["ingredient__name"]} - {ingredient["total"]}/'
                f'{ingredient["ingredient__measurement_unit"]} \n'
            ])
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={FILENAME}'
        return response
