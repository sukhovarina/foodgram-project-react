from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, SAFE_METHODS
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart, RecipeIngredient
from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateSerializer, FavoriteSerializer, ShoppingCartSerializer
)


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_list = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепт уже в избранном')
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            context = {'request': request}
            serializer = FavoriteSerializer(favorite, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not favorite_list.exists():
                raise exceptions.ValidationError('Рецепта нет в избранном')
            favorite_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        queryset = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            shopping_cart = ShoppingCart.objects.create(user=user, recipe=queryset)
            context = {'request': request}
            serializer = ShoppingCartSerializer(shopping_cart, context=context)
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
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        shopping_list = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )
        shopping_list_text = 'Список покупок:\n\n'
        for item in shopping_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            shopping_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        response = HttpResponse(shopping_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )

        return response
