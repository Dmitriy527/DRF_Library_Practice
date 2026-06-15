from rest_framework import serializers

from books.models import Book


class BookReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class BookListSerializer(BookReadSerializer):
    class Meta(BookReadSerializer.Meta):
        fields = "id", "title", "author"