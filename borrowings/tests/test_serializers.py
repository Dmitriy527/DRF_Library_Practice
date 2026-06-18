from datetime import date, timedelta
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from borrowings.serializers import (
    BorrowingReturnSerializer,
    BorrowingCreateSerializer,
    BorrowingReadSerializer,
)


def make_borrowing(
    borrow_date=None,
    expected_return=None,
    actual_return=None,
):
    """Return a lightweight mock that mimics a Borrowing instance."""
    today = date.today()
    obj = MagicMock()
    obj.borrow_date = borrow_date or today
    obj.expected_return = expected_return or (today + timedelta(days=7))
    obj.actual_return = actual_return
    return obj


def make_request(user_id=1, is_staff=False):
    """Return a minimal mock request."""
    user = MagicMock()
    user.id = user_id
    user.is_staff = is_staff
    request = MagicMock()
    request.user = user
    return request


def make_user(user_id=1):
    """Return a minimal mock user."""
    user = MagicMock()
    user.id = user_id
    return user


# ---------------------------------------------------------------------------
# BorrowingReturnSerializer
# ---------------------------------------------------------------------------

class BorrowingReturnSerializerValidateActualReturnTests(TestCase):

    def _get_serializer(self, instance):
        return BorrowingReturnSerializer(instance=instance)

    # --- already returned ---------------------------------------------------

    def test_raises_if_book_already_returned(self):
        """If actual_return is already set, validation must raise."""
        instance = make_borrowing(actual_return=date.today())
        s = self._get_serializer(instance)

        with self.assertRaises(DjangoValidationError):
            s.validate_actual_return(date.today())

    # --- None value ---------------------------------------------------------

    def test_raises_if_value_is_none(self):
        """Passing None as a return date must raise."""
        instance = make_borrowing()
        s = self._get_serializer(instance)

        with self.assertRaises(DRFValidationError):
            s.validate_actual_return(None)

    # --- date before borrow_date --------------------------------------------

    def test_raises_if_return_before_borrow_date(self):
        """A return date earlier than the borrow date must raise."""
        today = date.today()
        instance = make_borrowing(borrow_date=today)
        s = self._get_serializer(instance)

        with self.assertRaises(DRFValidationError):
            s.validate_actual_return(today - timedelta(days=1))

    # --- valid values -------------------------------------------------------

    def test_accepts_return_date_equal_to_borrow_date(self):
        """Returning on the same day as borrowing is valid."""
        today = date.today()
        instance = make_borrowing(borrow_date=today)
        s = self._get_serializer(instance)

        result = s.validate_actual_return(today)
        self.assertEqual(result, today)

    def test_accepts_return_date_after_borrow_date(self):
        """A normal future return date must pass validation."""
        today = date.today()
        instance = make_borrowing(borrow_date=today)
        s = self._get_serializer(instance)

        future = today + timedelta(days=3)
        result = s.validate_actual_return(future)
        self.assertEqual(result, future)


# ---------------------------------------------------------------------------
# BorrowingCreateSerializer – validate_user_id
# ---------------------------------------------------------------------------

class BorrowingCreateSerializerValidateUserIdTests(TestCase):

    def _get_serializer(self, request=None):
        context = {"request": request} if request else {}
        return BorrowingCreateSerializer(data={}, context=context)

    # --- staff user ---------------------------------------------------------

    def test_staff_can_create_for_any_user(self):
        """Staff users may assign any user_id."""
        request = make_request(user_id=1, is_staff=True)
        s = self._get_serializer(request)

        other_user = make_user(user_id=99)
        result = s.validate_user_id(other_user)
        self.assertEqual(result, other_user)

    # --- regular user -------------------------------------------------------

    def test_regular_user_can_create_for_themselves(self):
        """A non-staff user may create a borrowing for their own id."""
        request = make_request(user_id=5, is_staff=False)
        s = self._get_serializer(request)

        own_user = make_user(user_id=5)
        result = s.validate_user_id(own_user)
        self.assertEqual(result, own_user)

    def test_regular_user_cannot_create_for_other_user(self):
        """A non-staff user must not create borrowings for someone else."""
        request = make_request(user_id=5, is_staff=False)
        s = self._get_serializer(request)

        other_user = make_user(user_id=99)
        with self.assertRaises(DRFValidationError):
            s.validate_user_id(other_user)

    # --- no request in context ----------------------------------------------

    def test_no_request_in_context_passes_through(self):
        """When there is no request in context, any value passes unchanged."""
        s = self._get_serializer(request=None)
        user = make_user(user_id=7)
        result = s.validate_user_id(user)
        self.assertEqual(result, user)


# ---------------------------------------------------------------------------
# BorrowingCreateSerializer – __init__ queryset logic
# ---------------------------------------------------------------------------

class BorrowingCreateSerializerInitTests(TestCase):
    """
    These tests verify that __init__ restricts the user_id queryset for
    non-staff users.  They require a real database, so they inherit from
    django.test.TestCase and use Django's test runner.
    """

    @classmethod
    def setUpTestData(cls):
        # Import here to avoid circular imports at module level in test files
        from django.contrib.auth import get_user_model
        User = get_user_model()

        cls.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        cls.regular_user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

    def _make_request(self, user):
        request = MagicMock()
        request.user = user
        return request

    def _get_serializer(self, request):
        return BorrowingCreateSerializer(data={}, context={"request": request})

    def test_staff_user_gets_full_queryset(self):
        """Staff users should see all users in the user_id field queryset."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        request = self._make_request(self.staff_user)
        s = self._get_serializer(request)
        qs = s.fields["user_id"].queryset
        self.assertQuerySetEqual(
            qs.order_by("id"),
            User.objects.all().order_by("id"),
            transform=lambda x: x,
        )

    def test_regular_user_gets_restricted_queryset(self):
        """Non-staff users should only see themselves in the user_id queryset."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        request = self._make_request(self.regular_user)
        s = self._get_serializer(request)
        qs = s.fields["user_id"].queryset
        self.assertQuerySetEqual(
            qs,
            User.objects.filter(id=self.regular_user.id),
            transform=lambda x: x,
        )


# ---------------------------------------------------------------------------
# BorrowingReadSerializer – field exposure
# ---------------------------------------------------------------------------

class BorrowingReadSerializerFieldsTests(TestCase):

    EXPECTED_FIELDS = {
        "id",
        "borrow_date",
        "expected_return",
        "actual_return",
        "book_id",
        "user_id",
    }

    def test_exposes_expected_fields(self):
        s = BorrowingReadSerializer()
        self.assertEqual(set(s.fields.keys()), self.EXPECTED_FIELDS)

    def test_book_id_is_read_only(self):
        s = BorrowingReadSerializer()
        self.assertTrue(s.fields["book_id"].read_only)


# ---------------------------------------------------------------------------
# BorrowingReturnSerializer – field exposure
# ---------------------------------------------------------------------------

class BorrowingReturnSerializerFieldsTests(TestCase):

    def test_exposes_only_actual_return(self):
        s = BorrowingReturnSerializer()
        self.assertEqual(list(s.fields.keys()), ["actual_return"])


# ---------------------------------------------------------------------------
# BorrowingCreateSerializer – field exposure
# ---------------------------------------------------------------------------

class BorrowingCreateSerializerFieldsTests(TestCase):

    EXPECTED_FIELDS = {"borrow_date", "expected_return", "book_id", "user_id"}

    def test_exposes_expected_fields(self):
        s = BorrowingCreateSerializer()
        self.assertEqual(set(s.fields.keys()), self.EXPECTED_FIELDS)
