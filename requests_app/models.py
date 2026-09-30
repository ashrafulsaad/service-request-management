from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class ServiceRequest(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    citizen = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="service_requests",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="service_requests",
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    assigned_officer = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Attachment(models.Model):
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(upload_to="attachments/")

    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)