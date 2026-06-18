from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserManagerTests(TestCase):

    # --- create_user ---

    def test_create_user_success(self):
        user = User.objects.create_user(email="test@example.com", password="secret123")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("secret123"))

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(email="Test@EXAMPLE.COM", password="pass")
        self.assertEqual(user.email, "Test@example.com")

    def test_create_user_no_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="pass")

    def test_create_user_none_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="pass")

    def test_create_user_is_not_staff(self):
        user = User.objects.create_user(email="user@example.com", password="pass")
        self.assertFalse(user.is_staff)

    def test_create_user_is_not_superuser(self):
        user = User.objects.create_user(email="user@example.com", password="pass")
        self.assertFalse(user.is_superuser)

    def test_create_user_is_saved_to_db(self):
        User.objects.create_user(email="saved@example.com", password="pass")
        self.assertTrue(User.objects.filter(email="saved@example.com").exists())

    def test_create_user_without_password(self):
        user = User.objects.create_user(email="nopass@example.com")
        self.assertFalse(user.has_usable_password())

    def test_create_user_extra_fields(self):
        user = User.objects.create_user(
            email="extra@example.com", password="pass", first_name="John"
        )
        self.assertEqual(user.first_name, "John")

    # --- create_superuser ---

    def test_create_superuser_success(self):
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_is_saved_to_db(self):
        User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.assertTrue(User.objects.filter(email="admin@example.com").exists())

    def test_create_superuser_is_staff_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="pass", is_staff=False
            )

    def test_create_superuser_is_superuser_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="pass", is_superuser=False
            )

    def test_create_superuser_normalizes_email(self):
        user = User.objects.create_superuser(email="Admin@EXAMPLE.COM", password="pass")
        self.assertEqual(user.email, "Admin@example.com")


class UserModelTests(TestCase):

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields_are_empty(self):
        self.assertEqual(User.REQUIRED_FIELDS, [])

    def test_username_attribute_does_not_exist(self):
        user = User.objects.create_user(email="u@example.com", password="pass")
        self.assertIsNone(getattr(user, "username", None))

    def test_email_is_unique(self):
        User.objects.create_user(email="unique@example.com", password="pass1")
        with self.assertRaises(Exception):
            User.objects.create_user(email="unique@example.com", password="pass2")

    def test_str_representation(self):
        user = User.objects.create_user(email="str@example.com", password="pass")
        # AbstractUser.__str__ returns get_full_name() or email fallback
        self.assertIn("str@example.com", str(user))

    def test_is_active_default_true(self):
        user = User.objects.create_user(email="active@example.com", password="pass")
        self.assertTrue(user.is_active)

    def test_password_is_hashed(self):
        user = User.objects.create_user(email="hash@example.com", password="plaintext")
        self.assertNotEqual(user.password, "plaintext")

    def test_user_can_authenticate_with_correct_password(self):
        user = User.objects.create_user(email="auth@example.com", password="correct")
        self.assertTrue(user.check_password("correct"))

    def test_user_cannot_authenticate_with_wrong_password(self):
        user = User.objects.create_user(email="auth2@example.com", password="correct")
        self.assertFalse(user.check_password("wrong"))