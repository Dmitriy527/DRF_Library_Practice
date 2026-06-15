from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from book.models import Book
from book.serializers import (
    BookReadSerializer,
    BookListSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookReadSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self) -> object:
        if self.action == "list":
            return BookListSerializer
        else:
            return self.serializer_class
