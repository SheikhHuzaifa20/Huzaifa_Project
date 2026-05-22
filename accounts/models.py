from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('ANALYST', 'Analyst'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_teacher(self):
        return self.role == 'TEACHER'

    def is_student(self):
        return self.role == 'STUDENT'

    def is_analyst(self):
        return self.role == 'ANALYST'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
