import django_filters
from django_filters import AllValuesMultipleFilter
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    author = AllValuesMultipleFilter(field_name='author__id')
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    shoppingcart = filters.BooleanFilter(widget=BooleanWidget())
    favorite = filters.BooleanFilter(widget=BooleanWidget())

    class Meta:
        model = Recipe
        fields = (
            'author__id', 'tags__slug',
            'favorite',
        )
