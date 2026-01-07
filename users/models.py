from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    """
    Customized User model inheriting from AbstractUser model.

    Attributes:
        None

    Methods:   
        full_name: Returns the full name of the user.
    """
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    # add additional fields in here
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def last_project(self):
        #last submitted project from user
        return self.projects.order_by('-id').first()

    @property
    def booked_safety_training(self):
        #check if user has future safety training booked
        entry =self.safety_training_groups.filter(training_date__gte=timezone.now())
        if entry.exists():
            return entry.first()
        else:
            return None
    
    @property
    def mrbs_user(self):
        return User.objects.get_mrbs_user(self.email)
    
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

class UserProfile(models.Model):
    """
    Model representing the user profile.

    This model represents the user profile and extends the Django User model.
    It has a one-to-one relationship with the User model and has many-to-many
    relationship with the DegreeArea model.

    Attributes:
        user (OneToOneField): One-to-one relationship with the User model.
        degree_area (ManyToManyField): Many-to-many relationship with the DegreeArea model.
        academic_id (CharField): The academic ID of the user.
        phone (CharField): The phone number of the user.
        emergency_contact (CharField): The name of the user's emergency contact.
        emergency_phone (CharField): The phone number of the user's emergency contact.
    
    Properties:
        is_complete: Check if all the required fields are filled in the object.
    """

    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, primary_key=True
    )
    degree_area = models.ManyToManyField(
        "DegreeArea", help_text=_("Select all that apply")
    )
    academic_id = models.CharField(
        max_length=100, help_text=_("Your academic ID for UNICAMP users")
    )
    phone = models.CharField(max_length=15, help_text=_("Your phone number"))
    emergency_contact = models.CharField(
        max_length=100, help_text=_("Your emergency contact name")
    )
    emergency_phone = models.CharField(
        max_length=15, help_text=_("Your emergency contact phone number")
    )

    def __str__(self):
        return f"Profile for {self.user.get_full_name() or self.user.username}"

    @property
    def is_complete(self):
        """
        Check if all the required fields are filled in the object.

        Returns:
            bool: True if all the required fields are filled, False otherwise.
        """
        required_fields = ['degree_area', 'phone', 'emergency_contact', 'emergency_phone']
        return all(getattr(self, field) for field in required_fields)
      

class DegreeArea(models.Model):
    """
    Model representing the degree area.

    This model represents the degree area and has a single field 'area' which is a
    character field with a maximum length of 100. The model is used for many-to-many
    relationship with the UserProfile model.

    Attributes:
        area (CharField): The degree area of the user.
    """

    def __str__(self):
        return self.area

    area = models.CharField(max_length=100)


class Position(models.Model):
    """
    Model representing the user's position.

    This model represents the position of a user and has a single field 'position'
    which is a character field with a maximum length of 100. The model is used to
    store the position of a user in the system.


    The suggested positions are:
        Professor
        Researcher
        Post-Doc
        Graduate Student (Doctorate)
        Graduate Student (Masters)
        Undergraduate
        Company
        Other

    Attributes:
        position (CharField): The position of the user.
    """

    def __str__(self):
        return self.position

    position = models.CharField(max_length=100)




class SafetyTraining(models.Model):
    """
    Model representing the safety training of a user.
    
    This model represents the safety training of a user and has the following fields:
    - user: The user who has completed the safety training.
    - completion_date: The date when the user completed the safety training.
    - expiration_date: The date when the user's safety training expires.
    - notes: Optional field for additional notes about the safety training.
    """
    
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, primary_key=True
    )
    completion_date = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)  # Optional field for additional notes
    
    class Meta:
        verbose_name = _("Safety Training")
        verbose_name_plural = _("Safety Trainings")
    
    def __str__(self):
        return f"{self.user.username} - Safety Training"
    
    @property
    def is_expired(self):
        """Check if the safety training has expired."""
        if self.expiration_date is None:
            return False  # No expiration date means it doesn't expire
        return self.expiration_date < timezone.now()
    
    @property
    def is_pending(self):
        """Check if the safety training is still pending completion."""
        return self.completion_date is None
    
    @property
    def is_trained(self):
        """Check if the user is currently trained (completed and not expired)."""
        return (
            self.completion_date is not None and 
            not self.is_expired
        )
    
    @property
    def days_until_expiration(self):
        """Get the number of days until expiration, or None if no expiration date."""
        if self.expiration_date is None:
            return None
        delta = self.expiration_date - timezone.now()
        return delta.days if delta.days > 0 else 0


class SafetyTrainingGroup(models.Model):
    """
    Model representing a scheduled safety training session for multiple users.
    """
    training_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    users = models.ManyToManyField(
        "User", 
        related_name='safety_training_groups',
        blank=True
    )
    
    class Meta:
        verbose_name = _("Safety Training Group")
        verbose_name_plural = _("Safety Training Groups")
        ordering = ['training_date']
    
    def __str__(self):
        status = "Completed" if self.completed else "Scheduled"
        return f"Safety Training - {self.training_date.strftime('%Y-%m-%d %H:%M')} ({status})"
    
    @property
    def is_upcoming(self):
        """Check if the training session is scheduled for the future."""
        return self.training_date > timezone.now()
    
    @property
    def is_past_due(self):
        """Check if the training session date has passed but not marked as completed."""
        return self.training_date < timezone.now() and not self.completed
    
    @property
    def participant_count(self):
        """Get the number of users registered for this training session."""
        return self.users.count()
