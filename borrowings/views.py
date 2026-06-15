from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer, BorrowingCreateSerializer, BorrowingReturnSerializer,
)


class BorrowingsReturnViewSet(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = [
        IsAdminUser,
    ]

    def get(self, request, *args, **kwargs):
        borrowing = self.get_object()

        if borrowing.actual_return:
            message = f"Book already returned on {borrowing.actual_return}"
        else:
            message = "Please enter return date"

        return Response(
            {
                "message": message,
            }
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
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")
        current_user_id = self.request.user.id

        if user_id:
            user_id = self._params_to_ints(user_id)
            queryset = queryset.filter(user_id__in=user_id)
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

