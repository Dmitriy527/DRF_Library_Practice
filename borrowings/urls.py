from django.urls import path, include
from rest_framework import routers

from borrowings import views

routers = routers.DefaultRouter()

urlpatterns = [
    path("", include(routers.urls)),
    path("borrowings/", views.BorrowingsViewSet.as_view(), name="create_borrowing"),
    path(
        "borrowings/<int:pk>/", views.BorrowingsReadViewSet.as_view(), name="borrowing"
    ),
    path(
        "borrowings/<int:pk>/return/",
        views.BorrowingsReturnViewSet.as_view(),
        name="return_borrowing",
    ),
]

app_name = "borrowings"
