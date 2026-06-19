from django.test import TestCase
from decimal import Decimal

from book.models import Book
from book.serializers import BookReadSerializer, BookListSerializer


def create_book(**kwargs):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": Book.BookCover.HARD,
        "inventory": 5,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


class BookReadSerializerTest(TestCase):

    def setUp(self):
        self.book = create_book()

    def test_contains_all_expected_fields(self):
        serializer = BookReadSerializer(self.book)
        expected_fields = {
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee"
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_title_field_value(self):
        serializer = BookReadSerializer(self.book)
        self.assertEqual(serializer.data["title"], self.book.title)

    def test_author_field_value(self):
        serializer = BookReadSerializer(self.book)
        self.assertEqual(serializer.data["author"], self.book.author)

    def test_cover_field_value(self):
        serializer = BookReadSerializer(self.book)
        self.assertEqual(serializer.data["cover"], Book.BookCover.HARD)

    def test_inventory_field_value(self):
        serializer = BookReadSerializer(self.book)
        self.assertEqual(serializer.data["inventory"], self.book.inventory)

    def test_daily_fee_field_value(self):
        serializer = BookReadSerializer(self.book)
        self.assertEqual(Decimal(serializer.data["daily_fee"]),
                         self.book.daily_fee)

    def test_valid_data_creates_book(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": Book.BookCover.SOFT,
            "inventory": 3,
            "daily_fee": "2.00",
        }
        serializer = BookReadSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.title, data["title"])
        self.assertEqual(book.author, data["author"])

    def test_missing_required_field_is_invalid(self):
        data = {
            "title": "No Author Book",
            "cover": Book.BookCover.HARD,
            "inventory": 1,
        }
        serializer = BookReadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_fee", serializer.errors)

    def test_cover_defaults_to_hard_if_not_provided(self):
        data = {
            "title": "Default Cover",
            "author": "Some Author",
            "inventory": 2,
            "daily_fee": "1.00",
        }
        serializer = BookReadSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.cover, Book.BookCover.HARD)

    def test_invalid_cover_choice_is_rejected(self):
        data = {
            "title": "Bad Cover",
            "author": "Some Author",
            "cover": "Invalid",
            "inventory": 1,
            "daily_fee": "1.00",
        }
        serializer = BookReadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cover", serializer.errors)

    def test_negative_inventory_is_rejected(self):
        data = {
            "title": "Negative Inventory",
            "author": "Some Author",
            "cover": Book.BookCover.HARD,
            "inventory": -1,
            "daily_fee": "1.00",
        }
        serializer = BookReadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("inventory", serializer.errors)


class BookListSerializerTest(TestCase):

    def setUp(self):
        self.book = create_book()

    def test_contains_only_id_title_author_fields(self):
        serializer = BookListSerializer(self.book)
        self.assertEqual(set(serializer.data.keys()),
                         {"id", "title", "author"})

    def test_does_not_contain_cover_inventory_daily_fee(self):
        serializer = BookListSerializer(self.book)
        for field in ("cover", "inventory", "daily_fee"):
            self.assertNotIn(field, serializer.data)

    def test_title_field_value(self):
        serializer = BookListSerializer(self.book)
        self.assertEqual(serializer.data["title"], self.book.title)

    def test_author_field_value(self):
        serializer = BookListSerializer(self.book)
        self.assertEqual(serializer.data["author"], self.book.author)

    def test_id_field_matches_book_id(self):
        serializer = BookListSerializer(self.book)
        self.assertEqual(serializer.data["id"], self.book.id)

    def test_serializes_multiple_books(self):
        create_book(title="Second Book", author="Second Author")
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)
        self.assertEqual(len(serializer.data), 2)
        for item in serializer.data:
            self.assertEqual(set(item.keys()), {"id", "title", "author"})
