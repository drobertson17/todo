from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Member(models.Model):
    name = models.CharField(max_length=100)


class Priority(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Task(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.IntegerField(default=1)
    description = models.TextField(default='')