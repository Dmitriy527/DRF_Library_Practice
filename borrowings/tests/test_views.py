from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from borrowings.models import Borrowing
from book.models import Book

User = get_user_model()


def create_user(email="user@test.com", password="testpass123", is_staff=False):
    return User.objects.create_user(email=email, password=password, is_staff=is_staff)


def create_admin(email="admin@test.com", password="adminpass123"):
    return User.objects.create_user(email=email, password=password, is_staff=True)


def create_borrowing(user, book, borrow_date=None, expected_return=None, actual_return=None):
    return Borrowing.objects.create(
        user_id=user,
        book_id=book,
        borrow_date=borrow_date or date.today(),
        expected_return=expected_return or date.today() + timedelta(days=7),
        actual_return=actual_return,
    )


# ---------------------------------------------------------------------------
# BorrowingsViewSet  (GET list / POST create)
# ---------------------------------------------------------------------------

class BorrowingsViewSetListTests(APITestCase):
    """Tests for GET /borrowings/ – list endpoint."""

    def setUp(self):
        self.url = reverse("borrowings:create_borrowing")

        self.user1 = create_user(email="user1@test.com")
        self.user2 = create_user(email="user2@test.com")
        self.admin = create_admin()

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=1.00,
            cover="HARD"
        )

        self.b1 = create_borrowing(self.user1, self.book)
        self.b2 = create_borrowing(self.user2, self.book, actual_return=date.today())

    # -- authentication -------------------------------------------------------

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -- regular user sees only own borrowings --------------------------------

    def test_regular_user_sees_only_own_borrowings(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data["results"]]
        self.assertIn(self.b1.id, ids)
        self.assertNotIn(self.b2.id, ids)

    # -- admin sees all -------------------------------------------------------

    def test_admin_sees_all_borrowings(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data["results"]]
        self.assertIn(self.b1.id, ids)
        self.assertIn(self.b2.id, ids)

    # -- filtering by user_id (admin only makes sense) -----------------------

    def test_filter_by_user_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"user_id": str(self.user1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data["results"]]
        self.assertIn(self.b1.id, ids)
        self.assertNotIn(self.b2.id, ids)

    def test_filter_by_multiple_user_ids(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"user_id": f"{self.user1.id},{self.user2.id}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data["results"]]
        self.assertIn(self.b1.id, ids)
        self.assertIn(self.b2.id, ids)

    # -- filtering by is_active ----------------------------------------------

    def test_filter_is_active_true_returns_not_returned(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for b in response.data["results"]:
            self.assertIsNone(b.get("actual_return"))

    def test_filter_is_active_false_returns_returned(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"is_active": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for b in response.data["results"]:
            self.assertIsNotNone(b.get("actual_return"))

    def test_filter_is_active_case_insensitive(self):
        self.client.force_authenticate(user=self.admin)
        for value in ("True", "TRUE", "true"):
            response = self.client.get(self.url, {"is_active": value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class BorrowingsViewSetCreateTests(APITestCase):
    """Tests for POST /borrowings/ – create endpoint."""

    def setUp(self):
        self.url = reverse("borrowings:create_borrowing")
        self.user = create_user()
        self.book = Book.objects.create(
            title="Book2",
            author="Author2",
            inventory=3,
            daily_fee=2.00,
            cover="SOFT"
        )

    def test_unauthenticated_cannot_create(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_borrowing(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "book_id": self.book.id,
            "user_id": self.user.id,
            "borrow_date": str(date.today()),
            "expected_return": str(date.today() + timedelta(days=5)),
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.filter(user_id=self.user, book_id=self.book).count(), 1)

    def test_uses_create_serializer_for_post(self):
        """POST should use BorrowingCreateSerializer."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "book_id": self.book.id,
            "user_id": self.user.id,
            "borrow_date": str(date.today()),
            "expected_return": str(date.today() + timedelta(days=5)),
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# BorrowingsReadViewSet  (GET detail)
# ---------------------------------------------------------------------------

class BorrowingsReadViewSetTests(APITestCase):
    """Tests for GET /borrowings/<pk>/ – retrieve endpoint."""

    def setUp(self):
        self.user = create_user()
        self.other_user = create_user(email="other@test.com")
        self.admin = create_admin()

        self.book = Book.objects.create(
            title="Book3",
            author="Author3",
            inventory=2,
            daily_fee=1.50,
            cover="HARD"
        )
        self.borrowing = create_borrowing(self.user, self.book)
        self.url = reverse("borrowings:borrowing", kwargs={"pk": self.borrowing.pk})

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_retrieve_borrowing(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)

    def test_admin_can_retrieve_any_borrowing(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonexistent_borrowing_returns_404(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# BorrowingsReturnViewSet  (GET info + PATCH/PUT return)
# ---------------------------------------------------------------------------

class BorrowingsReturnViewSetTests(APITestCase):
    """Tests for GET/PATCH /borrowings/<pk>/return/ – return endpoint."""

    def setUp(self):
        self.user = create_user()
        self.admin = create_admin()

        self.book = Book.objects.create(
            title="Book4",
            author="Author4",
            inventory=4,
            daily_fee=3.00,
            cover="SOFT"
        )
        self.borrowing = create_borrowing(self.user, self.book)
        self.url = reverse("borrowings:return_borrowing", kwargs={"pk": self.borrowing.pk})

    # -- permissions ---------------------------------------------------------

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_access_return_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -- GET message ---------------------------------------------------------

    def test_get_returns_pending_message_when_not_returned(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Please enter return date", response.data["message"])

    def test_get_returns_already_returned_message(self):
        return_date = date.today()
        self.borrowing.actual_return = return_date
        self.borrowing.save()

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(return_date), response.data["message"])

    # -- PATCH / return action -----------------------------------------------

    def test_admin_can_set_return_date(self):
        self.client.force_authenticate(user=self.admin)
        return_date = str(date.today())
        response = self.client.patch(self.url, {"actual_return": return_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertEqual(str(self.borrowing.actual_return), return_date)

    def test_cannot_return_already_returned_borrowing(self):
        """Serializer validation should block re-return."""
        self.borrowing.actual_return = date.today()
        self.borrowing.save()

        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.url, {"actual_return": str(date.today())})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
