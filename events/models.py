from django.db import models
import uuid
import hashlib


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    venue = models.CharField(max_length=200, default='Main Auditorium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Participant(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    registered_at = models.DateTimeField(auto_now_add=True)
    attendance = models.BooleanField(default=False)
    feedback_submitted = models.BooleanField(default=False)
    certificate_hash = models.CharField(max_length=64, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.certificate_hash:
            raw = f"{self.student_id}-{self.email}-{uuid.uuid4()}"
            self.certificate_hash = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def eligible_for_certificate(self):
        return self.attendance and self.feedback_submitted

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.participant.name} — {self.rating}★"
