from django.db import models
from django.contrib.auth.models import User


# =========================
# Profile Model (User Role)
# =========================
class Profile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    bio = models.TextField(blank=True)

    # Freelancer Dashboard Fields
    experience = models.PositiveIntegerField(default=0)  # in years
    completed_projects = models.PositiveIntegerField(default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# =========================
# Job Model
# =========================
class Job(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()

    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# Application Model
# =========================
class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'freelancer')  # prevents duplicate applications

    def __str__(self):
        return f"{self.freelancer.username} → {self.job.title}"
