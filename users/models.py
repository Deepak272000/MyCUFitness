from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
import uuid

class UserManager(BaseUserManager):
    #basically here i am defining how regular users are created.
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)  # this thing is used to convert our input into lower case.
        extra_fields.setdefault("is_active", True)  # we are using this line to set users active by default
        user = self.model(email=email, **extra_fields)  #using this for creating user instance
        user.set_password(password)  #hashing the password
        user.save(using=self._db)  #save means we are saving our user in the database
        return user               # returning that user

# now let's create superuser(defining how superusers (admins) are created.)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)     # superusers must be from staff
        extra_fields.setdefault("is_superuser", True)  #giving all the permissions to superuser
        return self.create_user(email, password, **extra_fields)  #here i am calling create_user method


#here now we are switching to email based authentication.
class User(AbstractUser):
    username = None  # Removing default username field
    email = models.EmailField(unique=True)  # now here i am Using email as the unique identifier
    password = models.CharField(max_length=255)  #we can use maximum 255 characters in password field.
    two_factor_enabled = models.BooleanField(default=False)  #Now i am adding this line for 2fa usinf otp
    is_active = models.BooleanField(default=False)  # User is inactive until verified
    verification_token = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = str(uuid.uuid4())  # Generate token on creation
        super().save(*args, **kwargs)

    #this allow users to have different types of roles
    role_choices = [
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=role_choices, default='student')

# basically here i am using Json fields for storing structured data
    fitness_goals = models.JSONField(default=dict, blank=True, null=True)  #this line is for setting goals
    dietary_preferences = models.JSONField(default=dict, blank=True, null=True)  #our dietary pef>>>for e.g. veg nonveg, etc
    allergies = models.JSONField(default=dict, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
