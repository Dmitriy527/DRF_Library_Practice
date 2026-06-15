from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer, BorrowingCreateSerializer,
)


class BorrowingsViewSet(generics.ListCreateAPIView):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingReadSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
        queryset = self.queryset
        current_user_id = self.request.user.id

        if self.request.user.is_staff is False:
            queryset = queryset.filter(user_id=current_user_id)

        return queryset.distinct()


class BorrowingsReadViewSet(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [
        IsAuthenticated,
    ]

