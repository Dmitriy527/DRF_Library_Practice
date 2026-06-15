from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowings.models import Borrowing


class BorrowingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book_id",
            "user_id",
        ]

    book_id = BookReadSerializer(read_only=True)
