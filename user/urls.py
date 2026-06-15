from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from user import views

routers = routers.DefaultRouter()

urlpatterns = [
    path("", include(routers.urls)),
    path("users/", views.CreateUserView.as_view(), name="create"),
    path("me/", views.ManageUserView.as_view(), name="manage_user"),
    path("token/", views.LoginUserView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
]

app_name = "user"
