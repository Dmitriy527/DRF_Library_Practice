from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book.models import Book
from book.serializers import BookListSerializer, BookReadSerializer

User = get_user_model()

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


def sample_book(**kwargs):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "Hard",
        "inventory": 5,
        "daily_fee": 1.50,
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(APITestCase):
    """Tests for unauthenticated requests (read-only access)."""

    def test_list_books_allowed(self):
        """Unauthenticated users can retrieve the list of books."""
        sample_book()
        sample_book(title="Second Book")

        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_uses_list_serializer(self):
        """List action returns data matching BookListSerializer."""
        book = sample_book()

        response = self.client.get(BOOKS_URL)

        books = Book.objects.all().order_by("id")
        serializer = BookListSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_book_allowed(self):
        """Unauthenticated users can retrieve a single book."""
        book = sample_book()

        response = self.client.get(detail_url(book.id))

        serializer = BookReadSerializer(book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_forbidden(self):
        """Unauthenticated users cannot create books."""
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "Soft",
            "inventory": 3,
            "daily_fee": 2.00,
        }

        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_forbidden(self):
        """Unauthenticated users cannot update books."""
        book = sample_book()
        payload = {"title": "Updated Title"}

        response = self.client.patch(detail_url(book.id), payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_forbidden(self):
        """Unauthenticated users cannot delete books."""
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminBookApiTests(APITestCase):
    """Tests for authenticated non-admin users (read-only access)."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(self.user)

    def test_list_books_allowed(self):
        """Authenticated non-admin users can list books."""
        sample_book()

        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book_allowed(self):
        """Authenticated non-admin users can retrieve a book."""
        book = sample_book()

        response = self.client.get(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        """Non-admin authenticated users cannot create books."""
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "Soft",
            "inventory": 3,
            "daily_fee": 2.00,
        }

        response = self.client.post(BOOKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        """Non-admin authenticated users cannot update books."""
        book = sample_book()
        payload = {"title": "Updated Title"}

        response = self.client.patch(detail_url(book.id), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        """Non-admin authenticated users cannot delete books."""
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(APITestCase):
    """Tests for admin users (full CRUD access)."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123",
        )
        self.client.force_authenticate(self.admin)

    def test_list_books(self):
        """Admin can list all books."""
        sample_book()
        sample_book(title="Second Book")

        response = self.client.get(BOOKS_URL)

        books = Book.objects.all().order_by("id")
        serializer = BookListSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_book(self):
        """Admin can retrieve a single book using BookReadSerializer."""
        book = sample_book()

        response = self.client.get(detail_url(book.id))

        serializer = BookReadSerializer(book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book(self):
        """Admin can create a new book."""
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "Hard",
            "inventory": 10,
            "daily_fee": 3.00,
        }

        response = self.client.post(BOOKS_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=response.data["id"])
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.cover, payload["cover"])
        self.assertEqual(book.inventory, payload["inventory"])
        self.assertEqual(float(book.daily_fee), float(payload["daily_fee"]))

    def test_partial_update_book(self):
        """Admin can partially update a book."""
        book = sample_book()
        payload = {"title": "Updated Title", "inventory": 20}

        response = self.client.patch(detail_url(book.id), payload, format='json')

        book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.inventory, payload["inventory"])

    def test_full_update_book(self):
        """Admin can fully update a book."""
        book = sample_book()
        payload = {
            "title": "Fully Updated Book",
            "author": "New Author",
            "cover": "Soft",
            "inventory": 7,
            "daily_fee": 4.50,
        }

        response = self.client.put(detail_url(book.id), payload, format='json')

        book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.cover, payload["cover"])
        self.assertEqual(book.inventory, payload["inventory"])
        self.assertEqual(float(book.daily_fee), float(payload["daily_fee"]))

    def test_delete_book(self):
        """Admin can delete a book."""
        book = sample_book()

        response = self.client.delete(detail_url(book.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())


class BookSerializerSelectionTests(APITestCase):
    """Tests to verify correct serializer is used per action."""

    def test_list_action_uses_book_list_serializer(self):
        """BookListSerializer is used for list action."""
        from book.views import BookViewSet

        viewset = BookViewSet()
        viewset.action = "list"
        self.assertEqual(viewset.get_serializer_class(), BookListSerializer)

    def test_retrieve_action_uses_book_read_serializer(self):
        """BookReadSerializer is used for retrieve action."""
        from book.views import BookViewSet

        viewset = BookViewSet()
        viewset.action = "retrieve"
        self.assertEqual(viewset.get_serializer_class(), BookReadSerializer)

    def test_create_action_uses_book_read_serializer(self):
        """BookReadSerializer is used for create action."""
        from book.views import BookViewSet

        viewset = BookViewSet()
        viewset.action = "create"
        self.assertEqual(viewset.get_serializer_class(), BookReadSerializer)

    def test_update_action_uses_book_read_serializer(self):
        """BookReadSerializer is used for update action."""
        from book.views import BookViewSet

        viewset = BookViewSet()
        viewset.action = "update"
        self.assertEqual(viewset.get_serializer_class(), BookReadSerializer)
