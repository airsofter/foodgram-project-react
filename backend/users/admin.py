from django.contrib import admin

from users.models import User, Subscription
from recipes.models import Recipe


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'recipes_count',
        'followers_count'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'first_name', 'last_name')
    empty_value_display = '-пусто-'

    def recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def followers_count(self, obj):
        return Subscription.objects.filter(user=obj).count()


@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    list_editable = ('user', 'author')
    empty_value_display = '-пусто-'
