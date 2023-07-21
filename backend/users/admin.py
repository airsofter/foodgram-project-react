from django.contrib import admin

from users.models import User, Subscription


class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'first_name', 'last_name')
    empty_value_display = '-пусто-'


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    list_editable = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, UsersAdmin)
admin.site.register(Subscription, SubscriptionsAdmin)
