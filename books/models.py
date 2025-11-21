from django.conf import settings
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=500)
    openlibrary_id = models.CharField(max_length=100, blank=True, null=True)
    pages = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class Rental(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    months_rented = models.PositiveIntegerField(default=1)
    monthly_fee_cents = models.PositiveIntegerField(default=0)
    total_charged_cents = models.PositiveIntegerField(default=0)

    def compute_monthly_fee_from_pages(self):
        """
        Compute monthly fee based on book pages.
        Formula: (pages / 100) dollars converted to cents
        """
        if self.book.pages:
            return int((self.book.pages / 100.0) * 100)  # pages/100 dollars -> cents
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.months_rented} months)"
