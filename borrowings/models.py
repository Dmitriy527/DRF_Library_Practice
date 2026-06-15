from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return = models.DateField()
    actual_return = models.DateField(null=True, blank=True)
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )

    def clean(self):
        errors = {}

        if self.borrow_date and self.borrow_date < timezone.localdate():
            errors["borrow_date"] = "Borrow date cannot be in the past."

        if self.borrow_date and self.expected_return:
            if self.expected_return < self.borrow_date:
                errors["expected_return"] = (
                    "Expected return must be on or after borrow date."
                )

        if self.actual_return and self.borrow_date:
            if self.actual_return < self.borrow_date:
                errors["actual_return"] = "Actual return cannot be before borrow date."

        if errors:
            raise ValidationError(errors)
