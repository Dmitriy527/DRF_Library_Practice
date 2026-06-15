from rest_framework import viewsets

from book.models import Book
from book.permissions import IsAdminAndIsAuthenticatedOrReadOnly
from book.serializers import (
    BookReadSerializer,
    BookListSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookReadSerializer
    permission_classes = [IsAdminAndIsAuthenticatedOrReadOnly]

    def get_serializer_class(self) -> object:
        if self.action == "list":
            return BookListSerializer
        else:
            return self.serializer_class
