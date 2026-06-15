from django.core.exceptions import ValidationError
from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowings.models import Borrowing
from user.models import User


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "book_id",
            "user_id",
        ]
        read_only_fields = ("id",)
        user_id = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(), required=True
        )


    def create(self, validated_data):
        try:
            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


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
