from django.contrib import admin

from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ['id', 'email', 'username', 'first_name', 'last_name']
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ("pk", "user", "author")
    empty_value_display = '-empty-'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
