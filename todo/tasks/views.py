from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Task, Category, Member, Status


class TaskList(ListView):
    model = Task
    template_name = 'task_list.html'   # Optional if you follow naming conventions
    context_object_name = 'tasks'      # Default is 'object_list'

    def get_queryset(self):
        return Task.objects.select_related('category', 'assigned_to', 'status').all()
    

class NewTask(CreateView):
    model = Task
    fields = ['name', 'category', 'assigned_to', 'priority', 'description', 'status']
    template_name = 'new_task.html'
    success_url = reverse_lazy('task_list') 


class NewCategory(CreateView):
    model = Category
    fields = ['name']
    template_name = 'new_category.html'
    success_url = reverse_lazy('new_task') 


class NewMember(CreateView):
    model = Member
    fields = ['name']
    template_name = 'new_assignee.html'
    success_url = reverse_lazy('task_list') 


class NewStatus(CreateView):
    model = Status
    fields = ['name']
    template_name = 'new_status.html'
    success_url = reverse_lazy('task_list') 