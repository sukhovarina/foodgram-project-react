import django_filters
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='get_favorite', )
    is_in_shopping_cart = filters.BooleanFilter(method='get_shoppingcart', )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorite__user=self.request.user
            )
        return Recipe.objects.all()

    def get_shoppingcart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shoppingcart__user=self.request.user)
        return Recipe.objects.all()
