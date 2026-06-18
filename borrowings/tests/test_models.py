from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from book.models import Book
from borrowings.models import Borrowing
from user.models import User


def make_book(title="Test Book", inventory=5):
    return Book.objects.create(
        title=title,
        author="Author",
        cover="HARD",
        inventory=inventory,
        daily_fee=1.00,
    )


def make_user(email="user@test.com"):
    return User.objects.create_user(email=email, password="testpass123")


def make_borrowing(book, user, days_ahead=1, expected_days=7, actual_return=None):
    today = timezone.localdate()
    return Borrowing(
        borrow_date=today + timedelta(days=days_ahead),
        expected_return=today + timedelta(days=expected_days),
        actual_return=actual_return,
        book_id=book,
        user_id=user,
    )


class BorrowingValidateInventoryTest(TestCase):
    def setUp(self):
        self.book = make_book(inventory=0)

    def test_raises_error_when_inventory_is_zero(self):
        with self.assertRaises(ValidationError):
            Borrowing.validate_inventory(self.book, ValidationError)

    def test_no_error_when_inventory_is_positive(self):
        self.book.inventory = 1
        # Should not raise
        Borrowing.validate_inventory(self.book, ValidationError)

    def test_error_message_contains_book_title(self):
        with self.assertRaises(ValidationError) as ctx:
            Borrowing.validate_inventory(self.book, ValidationError)
        self.assertIn(self.book.title, str(ctx.exception))


class BorrowingCleanTest(TestCase):
    def setUp(self):
        self.book = make_book()
        self.user = make_user()
        self.today = timezone.localdate()

    def test_borrow_date_in_past_raises_error(self):
        b = make_borrowing(self.book, self.user, days_ahead=1)
        b.borrow_date = self.today - timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            b.clean()
        self.assertIn("borrow_date", ctx.exception.message_dict)

    def test_expected_return_before_borrow_date_raises_error(self):
        b = make_borrowing(self.book, self.user, days_ahead=3, expected_days=1)
        with self.assertRaises(ValidationError) as ctx:
            b.clean()
        self.assertIn("expected_return", ctx.exception.message_dict)

    def test_actual_return_before_borrow_date_raises_error(self):
        b = make_borrowing(self.book, self.user, days_ahead=3, expected_days=5)
        b.actual_return = self.today + timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            b.clean()
        self.assertIn("actual_return", ctx.exception.message_dict)

    def test_valid_data_passes_clean(self):
        b = make_borrowing(self.book, self.user, days_ahead=1, expected_days=7)
        b.clean()

    def test_expected_return_equal_to_borrow_date_is_valid(self):
        b = make_borrowing(self.book, self.user, days_ahead=2, expected_days=2)
        b.clean()

    def test_actual_return_equal_to_borrow_date_is_valid(self):
        b = make_borrowing(self.book, self.user, days_ahead=1, expected_days=5)
        b.actual_return = b.borrow_date
        b.clean()

    def test_multiple_errors_raised_together(self):
        b = make_borrowing(self.book, self.user, days_ahead=1)
        b.borrow_date = self.today - timedelta(days=2)
        b.expected_return = self.today - timedelta(days=5)
        with self.assertRaises(ValidationError) as ctx:
            b.clean()
        errors = ctx.exception.message_dict
        self.assertIn("borrow_date", errors)
        self.assertIn("expected_return", errors)


class BorrowingSaveNewTest(TestCase):
    def setUp(self):
        self.book = make_book(inventory=3)
        self.user = make_user()

    def test_inventory_decremented_on_create(self):
        b = make_borrowing(self.book, self.user)
        b.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_borrowing_saved_to_db_on_create(self):
        b = make_borrowing(self.book, self.user)
        b.save()
        self.assertTrue(Borrowing.objects.filter(pk=b.pk).exists())

    def test_zero_inventory_raises_integrity_error_on_create(self):
        self.book.inventory = 0
        self.book.save()
        b = make_borrowing(self.book, self.user)
        with self.assertRaises(IntegrityError):
            b.save()

    def test_inventory_not_changed_when_save_fails(self):
        self.book.inventory = 0
        self.book.save()
        b = make_borrowing(self.book, self.user)
        try:
            b.save()
        except IntegrityError:
            pass
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 0)

    def test_past_borrow_date_raises_validation_error(self):
        b = make_borrowing(self.book, self.user)
        b.borrow_date = timezone.localdate() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            b.save()


class BorrowingSaveUpdateTest(TestCase):
    def setUp(self):
        self.book = make_book(inventory=3)
        self.user = make_user()
        self.borrowing = make_borrowing(self.book, self.user)
        self.borrowing.save()
        self.book.refresh_from_db()

    def test_inventory_incremented_on_return(self):
        inventory_before = self.book.inventory
        self.borrowing.actual_return = timezone.localdate()
        self.borrowing.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory_before + 1)

    def test_inventory_not_incremented_if_already_returned(self):
        self.borrowing.actual_return = timezone.localdate()
        self.borrowing.save()
        self.book.refresh_from_db()
        inventory_after_first_return = self.book.inventory

        self.borrowing.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory_after_first_return)

    def test_atomic_transaction_rolls_back_on_error(self):
        inventory_before = self.book.inventory
        with patch.object(Borrowing, "full_clean", side_effect=ValidationError("err")):
            new_b = make_borrowing(self.book, self.user)
            try:
                new_b.save()
            except ValidationError:
                pass
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory_before)
