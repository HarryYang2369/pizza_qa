import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    email = models.EmailField(unique=True)
    real_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    year = models.IntegerField(null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['real_name', 'role']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # For new student users, generate nickname after saving
        is_new = self._state.adding
        super().save(*args, **kwargs)
    
        if is_new and self.role == 'student' and not self.nickname:
            self.nickname = f"Student_{self.id}"
            # Save just the nickname field to avoid recursion
            self.save(update_fields=['nickname'])
    
    def get_available_subjects(self):
        """Get subjects available for the user based on their role."""
        if self.role == 'teacher':
            return self.taught_subjects.all()
        elif self.role == 'student':
            return self.enrolled_subjects.all()
        return []

@receiver(post_save, sender=CustomUser)
def set_student_nickname(sender, instance, created, **kwargs):
    """Signal to set nickname for new student users"""
    if created and instance.role == 'student' and not instance.nickname:
        # Nickname will be set in the save method
        pass