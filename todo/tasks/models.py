from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Member(models.Model):
    name = models.CharField(max_length=100, unique=True)
    avatar = models.CharField(max_length=10, default="👤")
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Members"
    
    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=100, unique=True)
    level = models.IntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    color = models.CharField(max_length=7, default="#6c757d")
    
    class Meta:
        verbose_name_plural = "Priorities"
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} ({self.level})"


class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#6c757d")
    is_completed = models.BooleanField(default=False, help_text="Mark as completed status")
    order = models.IntegerField(default=0, help_text="Display order in kanban board")
    
    class Meta:
        verbose_name_plural = "Statuses"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    # Time tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_overdue(self):
        if self.due_date and not self.status.is_completed if self.status else False:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    def mark_completed(self):
        if self.status and self.status.is_completed:
            self.completed_at = timezone.now()
            self.save()


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.name} on {self.task.name}"


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.file_name