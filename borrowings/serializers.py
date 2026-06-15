from django.core.exceptions import ValidationError
from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowings.models import Borrowing
from user.models import User


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "actual_return",
        ]

    def validate_actual_return(self, value):
        instance = self.instance

        if instance.actual_return is not None:
            raise ValidationError(
                {"message": f"Book already returned on {instance.actual_return}"}
            )

        if value is None:
            raise serializers.ValidationError(f"Return date cannot be None")

        if value < instance.borrow_date:
            raise serializers.ValidationError(
                f"Return date cannot be earlier than borrow date ({instance.borrow_date})"
            )

        return value


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and not request.user.is_staff:
            self.fields["user_id"].queryset = User.objects.filter(id=request.user.id)
            self.fields["user_id"].initial = request.user.id
        else:
            self.fields["user_id"].queryset = User.objects.all()

    def validate_user_id(self, value):
        request = self.context.get("request")

        if request and not request.user.is_staff:
            if value.id != request.user.id:
                raise serializers.ValidationError(
                    "A regular user can create loans only for themselves"
                )
        return value

    def create(self, validated_data):
        try:
            return Borrowing.objects.create(**validated_data)
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
