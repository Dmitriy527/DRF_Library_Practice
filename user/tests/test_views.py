from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

CREATE_USER_URL = reverse("user:create")
LOGIN_USER_URL = reverse("user:get_token")
ME_URL = reverse("user:manage_user")


def create_user(**params):
    defaults = {
        "email": "test@example.com",
        "password": "testpassword123",
    }
    defaults.update(params)
    return User.objects.create_user(**defaults)


def auth_header(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZE": f"Bearer {token.access_token}"}


class CreateUserViewTests(APITestCase):
    """Tests for POST /user/create/"""

    def test_create_user_success(self):
        payload = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_create_user_no_authentication_required(self):
        """Endpoint must be publicly accessible."""
        payload = {
            "email": "public@example.com",
            "password": "publicpass123",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_missing_email_fails(self):
        res = self.client.post(
            CREATE_USER_URL,
            {"password": "somepass123"}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_password_fails(self):
        res = self.client.post(
            CREATE_USER_URL,
            {"email": "nopass@example.com"}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginUserViewTests(APITestCase):
    """Tests for POST /user/token/ (TokenObtainPairView)."""

    def setUp(self):
        self.user = create_user(
            email="login@example.com",
            password="loginpass123"
        )

    def test_login_returns_tokens(self):
        payload = {
            "email": "login@example.com",
            "password": "loginpass123"
        }
        res = self.client.post(LOGIN_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_wrong_password_fails(self):
        payload = {
            "email": "login@example.com",
            "password": "wrongpassword"
        }
        res = self.client.post(LOGIN_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", res.data)

    def test_login_nonexistent_user_fails(self):
        payload = {
            "email": "ghost@example.com",
            "password": "somepassword"
        }
        res = self.client.post(LOGIN_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_no_authentication_required(self):
        """Login endpoint must be publicly accessible."""
        payload = {
            "email": "login@example.com",
            "password": "loginpass123"
        }
        res = self.client.post(LOGIN_USER_URL, payload)

        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_missing_credentials_fails(self):
        res = self.client.post(LOGIN_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ManageUserViewTests(APITestCase):
    """Tests for GET/PATCH /user/me/."""

    def setUp(self):
        self.user = create_user(
            email="me@example.com",
            first_name="Dimka",
            last_name="nividimka",
            password="mepassword123",
        )
        self.client.credentials(**auth_header(self.user))

    def test_retrieve_user_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertNotIn("mepassword123", res.data["password"])

    def test_retrieve_profile_unauthenticated_fails(self):
        self.client.credentials()  # clear auth
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_success(self):
        payload = {"password": "newstrongpassword456"}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_post_method_not_allowed(self):
        """
        ManageUserView inherits RetrieveUpdateAPIView
        — POST must be rejected.
        """
        res = self.client.post(
            ME_URL,
            {"email": "should@fail.com"}
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_user_cannot_retrieve_other_users_profile(self):
        """get_object always returns request.user, never another user."""
        other_user = create_user(
            email="other@example.com",
            password="otherpassword123"
        )
        self.client.credentials(**auth_header(other_user))
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], other_user.email)
        self.assertNotEqual(res.data["email"], self.user.email)
