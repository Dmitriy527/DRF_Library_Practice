from django.db import models


class Book(models.Model):
    class Meta:
        verbose_name_plural = "Books"

    class BookCover(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        max_length=20,
        choices=BookCover.choices,
        default=BookCover.HARD,
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    def __str__(self):
        return self.title + " - " + self.author
