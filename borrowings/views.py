from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer, BorrowingCreateSerializer,
)


class BorrowingsViewSet(generics.ListCreateAPIView):
    queryset = Borrowing.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingReadSerializer
        return BorrowingCreateSerializer


class BorrowingsReadViewSet(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [
        IsAuthenticated,
    ]

