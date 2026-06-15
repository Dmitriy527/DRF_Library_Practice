from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
)


class BorrowingsViewSet(generics.ListCreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [AllowAny]


class BorrowingsReadViewSet(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [
        IsAuthenticated,
    ]

