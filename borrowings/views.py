from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
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

@extend_schema_view(
    get = extend_schema(
        responses={200: BorrowingReadSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by user_id",
                examples=[
                    OpenApiExample(
                        "Example",
                        summary="user_id = 1,2",
                        description="You must enter the user ID number or numbers separated by commas.",
                        value="1,2",
                    ),
                ],
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtering by users whose loan status is active or inactive",
                examples=[
                    OpenApiExample(
                        "Example 1",
                        summary="is_active = true",
                        description="You need to enter whether the loan is active - true",
                        value="true",
                    ),
                    OpenApiExample(
                        "Example 2",
                        summary="is_active = false",
                        description="You need to enter whether the loan is inactive - false",
                        value="false",
                    ),
                ],
            ),
        ],
        auth=None,
        operation_id=None,
        operation=None,
        examples=[
            OpenApiExample(
                "Description how to use the parameters",
                description="In this route, at the very end, after the question mark,"
                            + "separated by an ampersand, you can specify the following "
                            + "parameters: page, is_active, and user_id. The page and "
                            + "is_active parameters can change what is displayed for "
                            + "any registered user, while the user_id parameter will change"
                            + " what is displayed only if the user is an administrator.",
                value={
                    "id": 1,
                    "borrow_date": "2026-06-19",
                    "expected_return": "2026-06-20",
                    "actual_return": "null or 2026-06-21",
                    "book_id": {
                        "id": 1,
                        "title": "Titanic",
                        "author": "Jamse Kameron",
                        "cover": "Hard",
                        "inventory": 6,
                        "daily_fee": "1.00"
                    },
                    "user_id": 3
                },
            ),
        ],
    ),
    post = extend_schema(
        responses={201: BorrowingCreateSerializer},
        description="Create a new borrowing"
    )
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
            if is_active:
                if is_active.lower() == "true":
                    queryset = queryset.filter(actual_return__isnull=True)
                elif is_active.lower() == "false":
                    queryset = queryset.filter(actual_return__isnull=False)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user_id=current_user_id)

        return queryset.distinct()


class BorrowingsReadViewSet(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [
        IsAuthenticated,
    ]
