from django.urls import include, path
from rest_framework import routers

from users import views

app_name = 'users'

router = routers.DefaultRouter()
router.register('users', views.CustomUserViewSet, basename="users")

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
