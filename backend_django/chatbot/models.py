from django.db import models


class FAQ(models.Model):
    """A single FAQ entry: one question, one answer, an optional category.

    `is_active` lets support staff soft-disable a FAQ (e.g. a seasonal promo
    that ended) from the admin panel without deleting its history.
    """

    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=80, blank=True, default="General")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "id"]

    def __str__(self):
        return self.question[:60]
