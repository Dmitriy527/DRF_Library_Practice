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

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        current_user_id = self.request.user.id

        if is_active:
            if is_active is not None:
                if is_active.lower() == "true":
                    queryset = queryset.filter(actual_return__isnull=True)
                elif is_active.lower() == "false":
                    queryset = queryset.filter(actual_return__isnull=False)
        if self.request.user.is_staff is False:
            queryset = queryset.filter(user_id=current_user_id)

        return queryset.distinct()


class BorrowingsReadViewSet(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [
        IsAuthenticated,
    ]

