from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models

GENDER_CHOICES = (("male", "Male"), ("female", "Female"))

class UserManager (BaseUserManager):
    # Define a model manager for User model with no username field
    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        # create user with email and password
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        # create regular User
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        # create SuperUser account
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    username = None
    role = models.CharField(max_length=12, error_messages={'required': 'Please select your role'})
    gender = models.CharField(max_length=10, blank=True, null=True, default="")
    email = models.EmailField(unique=True, blank=False, error_messages={'unique': 'User with this email already exist'})
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __unicode__ (self):
        return self.email
    
    objects = UserManager()