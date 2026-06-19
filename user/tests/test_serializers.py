from django.contrib.auth import get_user_model
from django.test import TestCase


from user.serializers import UserSerializer

User = get_user_model()


class UserSerializerCreateTests(TestCase):
    """Tests for UserSerializer create functionality."""

    def setUp(self):
        self.valid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }

    def test_create_user_with_valid_data(self):
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.last_name, self.valid_data["last_name"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_password_is_hashed_on_create(self):
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertNotEqual(user.password, self.valid_data["password"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_id_and_is_staff_are_read_only(self):
        data = {**self.valid_data, "id": 9999, "is_staff": True}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertNotEqual(user.id, 9999)
        self.assertFalse(user.is_staff)

    def test_create_user_without_optional_fields(self):
        data = {"email": "minimal@example.com", "password": "pass12345"}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, "minimal@example.com")

    def test_email_field_is_required(self):
        data = {**self.valid_data}
        del data["email"]
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_field_is_required(self):
        data = {**self.valid_data}
        del data["password"]
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_exactly_min_length_is_valid(self):
        data = {**self.valid_data, "password": "abc12"}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_email_format(self):
        data = {**self.valid_data, "email": "not-an-email"}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class UserSerializerUpdateTests(TestCase):
    """Tests for UserSerializer update functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="existing@example.com",
            password="oldpassword123",
            first_name="Old",
            last_name="Name",
        )

    def test_update_user_fields(self):
        data = {
            "email": "updated@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }
        serializer = UserSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertEqual(updated_user.email, "updated@example.com")
        self.assertEqual(updated_user.first_name, "New")
        self.assertEqual(updated_user.last_name, "User")

    def test_update_password_is_hashed(self):
        data = {"email": self.user.email, "password": "newpassword123"}
        serializer = UserSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password("newpassword123"))
        self.assertFalse(updated_user.check_password("oldpassword123"))

    def test_partial_update_without_password(self):
        old_password_hash = self.user.password
        serializer = UserSerializer(
            self.user, data={"first_name": "Updated"}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.password, old_password_hash)

    def test_partial_update_password_only(self):
        serializer = UserSerializer(
            self.user, data={"password": "brandnewpass"}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password("brandnewpass"))


class UserSerializerSerializationTests(TestCase):
    """Tests for UserSerializer output/representation."""

    def test_serialized_output_contains_expected_fields(self):
        user = User.objects.create_user(
            email="output@example.com",
            password="pass12345",
            first_name="Jane",
            last_name="Smith",
        )
        serializer = UserSerializer(user)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("first_name", data)
        self.assertIn("last_name", data)
        self.assertIn("is_staff", data)

    def test_is_staff_defaults_to_false(self):
        user = User.objects.create_user(email="staff@example.com",
                                        password="pass12345")
        serializer = UserSerializer(user)

        self.assertFalse(serializer.data["is_staff"])

    def test_password_whitespace_is_preserved(self):
        data = {
            "email": "ws@example.com",
            "password": "pass with spaces",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.check_password("pass with spaces"))
