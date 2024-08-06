from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db import models
from django.conf import settings

class UserManager(BaseUserManager):
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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='подписчик')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='user_set', related_query_name='user')
    objects = UserManager()
    user_permissions = models.ManyToManyField('auth.Permission',
                                              blank=True, related_name='user_set', related_query_name='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_author(self):
        return self.role == 'автор'


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)  # Add this field

    def save(self, *args, **kwargs):
        if not self.author.is_author():
            raise PermissionError("Only users with the role 'автор' can create articles.")
        super().save(*args, **kwargs)

    def can_edit(self, user):
        return self.author == user

    def can_delete(self, user):
        return self.author == user

    def can_read(self, user=None):
        if self.is_public:
            return True
        if user is None or self.is_closed and user.role != 'подписчик':
            return False
        return True

    def is_public_article(self):
        return self.is_public