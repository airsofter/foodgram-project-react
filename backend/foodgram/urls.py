from django.contrib import admin
from django.urls import path, include

# 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
]
