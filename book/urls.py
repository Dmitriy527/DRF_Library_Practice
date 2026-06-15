from django.urls import path, include
from rest_framework import routers

from book.views import BookViewSet

routers = routers.DefaultRouter()
routers.register("books", BookViewSet)

urlpatterns = [
    path("", include(routers.urls)),
]

app_name = "books"
