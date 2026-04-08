import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        # We don't have is_superuser or is_staff in your schema
        # but if we wanted to support standard admin we would need them.
        # We'll just define this minimal required method for manage.py createsuperuser to not crash.
        user = self.create_user(email, username, password, **extra_fields)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    # Mapping to your precise schema
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=255, unique=True)
    
    # Shadowing Django's default 'password' field to use your 'password_hash' column
    password = models.CharField(max_length=128, db_column='password_hash')
    
    full_name = models.CharField(max_length=100, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Disable last_login since it's not in your schema
    last_login = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
