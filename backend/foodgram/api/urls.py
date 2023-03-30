from django.urls import path, include
from rest_framework import routers

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

api_name = 'api'
router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
