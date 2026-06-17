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

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diaries')
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    emotion = models.CharField(max_length=50, blank=True, null=True)
    intensity = models.IntegerField(default=5)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'diaries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Diary of {self.user.username} at {self.created_at}"


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default='Cuộc trò chuyện mới')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat Session {self.id} of {self.user.username}"

class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.text[:20]}"



class Test(models.Model):
    TYPE_CHOICES = (
        ('clinical', 'Clinical'),
        ('personality', 'Personality'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tests'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    order_number = models.IntegerField(default=0)
    dimension = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'test_questions'
        ordering = ['order_number', 'id']

    def __str__(self):
        return f"{self.test.name} - Q{self.order_number}"

class QuestionOption(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'question_options'
        ordering = ['id']

    def __str__(self):
        return self.option_text

class TestResult(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    answers = models.JSONField(default=list)
    raw_result = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_results'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.created_at.date()})"
