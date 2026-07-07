import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email

class Photo(models.Model):
    """Separate table for photo metadata (best practice for cloud storage)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storage_url = models.URLField(max_length=500)  # S3/Cloudinary URL
    file_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

class Submission(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE, related_name='submission')  # 1:1 for now

    # User-provided metadata
    name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()  # 0-32767
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    place_of_living = models.CharField(max_length=255)
    country_of_origin = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # CRITICAL: Safety Rules.
    # Using JSON to store flexible rules like {"visibility": "private", "allow_download": false, "max_views": 100}
    safety_rules = models.JSONField(default=dict, blank=True)

    # CRITICAL: Classification result stored as structured JSON. 
    # Example: {"label": "cat", "confidence": 0.98, "model_version": "v2"}
    classification_result = models.JSONField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # For indexing
            models.Index(fields=['age']),
            models.Index(fields=['gender']),
            models.Index(fields=['country_of_origin']),
            models.Index(fields=['place_of_living']),
            models.Index(fields=['created_at']),  # For sorting
            models.Index(fields=['country_of_origin', 'gender']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission {self.id} by {self.user.email}"