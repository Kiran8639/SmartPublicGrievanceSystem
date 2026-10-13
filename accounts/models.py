from django.db import models
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        DEPARTMENT_STAFF = 'DEPARTMENT_STAFF', 'Department Staff'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    department = models.ForeignKey(
    Department,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='staff_members'
    )

    def __str__(self):
        return self.username
    
class Complaint(models.Model):

    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    photo = models.ImageField(
    upload_to='complaint_photos/',
    blank=True,
    null=True
    )

    citizen = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )

    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.NEW
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class ComplaintStatusHistory(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    old_status = models.CharField(
        max_length=15,
        choices=Complaint.Status.choices
    )

    new_status = models.CharField(
        max_length=15,
        choices=Complaint.Status.choices
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaint_status_changes'
    )

    note = models.TextField(blank=True)

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Complaint #{self.complaint_id}: {self.old_status} → {self.new_status}"

class Notification(models.Model):
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='notifications'
    )


    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message
