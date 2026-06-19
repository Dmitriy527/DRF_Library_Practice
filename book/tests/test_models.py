from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from book.models import Book


class BookModelTest(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title="Kobzar",
            author="Taras Shevchenko",
            cover=Book.BookCover.HARD,
            inventory=5,
            daily_fee=Decimal("1.99"),
        )

    # --- __str__ ---

    def test_str_returns_title_and_author(self):
        self.assertEqual(str(self.book), "Kobzar - Taras Shevchenko")

    # --- Default values ---

    def test_default_cover_is_hard(self):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            daily_fee=Decimal("2.50"),
        )
        self.assertEqual(book.cover, Book.BookCover.HARD)

    def test_default_inventory_is_zero(self):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            daily_fee=Decimal("2.50"),
        )
        self.assertEqual(book.inventory, 0)

    # --- BookCover choices ---

    def test_cover_hard_choice(self):
        self.book.cover = Book.BookCover.HARD
        self.book.save()
        self.assertEqual(self.book.cover, "Hard")

    def test_cover_soft_choice(self):
        self.book.cover = Book.BookCover.SOFT
        self.book.save()
        self.assertEqual(self.book.cover, "Soft")

    def test_book_cover_choices_count(self):
        self.assertEqual(len(Book.BookCover.choices), 2)

    # --- Field values ---

    def test_title_saved_correctly(self):
        self.assertEqual(self.book.title, "Kobzar")

    def test_author_saved_correctly(self):
        self.assertEqual(self.book.author, "Taras Shevchenko")

    def test_inventory_saved_correctly(self):
        self.assertEqual(self.book.inventory, 5)

    def test_daily_fee_saved_correctly(self):
        self.assertEqual(self.book.daily_fee, Decimal("1.99"))

    # --- Field constraints ---

    def test_title_max_length(self):
        max_length = Book._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_author_max_length(self):
        max_length = Book._meta.get_field("author").max_length
        self.assertEqual(max_length, 100)

    def test_daily_fee_max_digits(self):
        field = Book._meta.get_field("daily_fee")
        self.assertEqual(field.max_digits, 5)

    def test_daily_fee_decimal_places(self):
        field = Book._meta.get_field("daily_fee")
        self.assertEqual(field.decimal_places, 2)

    def test_inventory_does_not_allow_negative(self):
        book = Book(
            title="Negative Inventory",
            author="Author",
            inventory=-1,
            daily_fee=Decimal("1.00"),
        )
        with self.assertRaises(IntegrityError):
            book.save()

    # --- CRUD ---

    def test_book_is_created(self):
        self.assertIsNotNone(self.book.pk)

    def test_book_can_be_retrieved(self):
        fetched = Book.objects.get(pk=self.book.pk)
        self.assertEqual(fetched.title, self.book.title)

    def test_book_can_be_updated(self):
        self.book.title = "Updated Title"
        self.book.save()
        updated = Book.objects.get(pk=self.book.pk)
        self.assertEqual(updated.title, "Updated Title")

    def test_book_can_be_deleted(self):
        pk = self.book.pk
        self.book.delete()
        self.assertFalse(Book.objects.filter(pk=pk).exists())

    # --- Meta ---

    def test_verbose_name_plural(self):
        self.assertEqual(Book._meta.verbose_name_plural,
                         "Books")
