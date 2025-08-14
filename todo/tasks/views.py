from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from datetime import datetime, timedelta
from .models import Task, Status, Member, Category, Priority, TaskComment
from .forms import (
    MemberForm, StatusForm, TaskForm, CategoryForm, 
    PriorityForm, TaskCommentForm, TaskSearchForm
)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'category', 'assigned_to', 'status', 'priority'
        ).filter(is_archived=False)
        
        # Apply search and filters
        form = TaskSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            search_in = form.cleaned_data.get('search_in')
            category = form.cleaned_data.get('category')
            status = form.cleaned_data.get('status')
            priority = form.cleaned_data.get('priority')
            assigned_to = form.cleaned_data.get('assigned_to')
            due_date_from = form.cleaned_data.get('due_date_from')
            due_date_to = form.cleaned_data.get('due_date_to')
            show_overdue = form.cleaned_data.get('show_overdue')
            show_archived = form.cleaned_data.get('show_archived')
            
            if search_query:
                if search_in == 'name':
                    queryset = queryset.filter(name__icontains=search_query)
                elif search_in == 'description':
                    queryset = queryset.filter(description__icontains=search_query)
                elif search_in == 'tags':
                    queryset = queryset.filter(tags__icontains=search_query)
                elif search_in == 'assigned_to':
                    queryset = queryset.filter(assigned_to__name__icontains=search_query)
            
            if category:
                queryset = queryset.filter(category=category)
            if status:
                queryset = queryset.filter(status=status)
            if priority:
                queryset = queryset.filter(priority=priority)
            if assigned_to:
                queryset = queryset.filter(assigned_to=assigned_to)
            if due_date_from:
                queryset = queryset.filter(due_date__gte=due_date_from)
            if due_date_to:
                queryset = queryset.filter(due_date__lte=due_date_to)
            if show_overdue:
                queryset = queryset.filter(due_date__lt=datetime.now())
            if show_archived:
                queryset = Task.objects.select_related(
                    'category', 'assigned_to', 'status', 'priority'
                ).all()
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statuses and tasks grouped by status for kanban view
        statuses = Status.objects.all().order_by('order', 'name')
        status_tasks = []
        
        for status in statuses:
            tasks = self.get_queryset().filter(status=status)
            status_tasks.append((status, tasks))
        
        context['status_tasks'] = status_tasks
        
        # Forms and data for modals
        context['task_form'] = TaskForm()
        context['category_form'] = CategoryForm()
        context['assignee_form'] = MemberForm()
        context['status_form'] = StatusForm()
        context['priority_form'] = PriorityForm()
        context['search_form'] = TaskSearchForm(self.request.GET)
        
        # Additional context
        context['assignees'] = Member.objects.all().order_by('name')
        context['statuses'] = statuses
        context['categories'] = Category.objects.all().order_by('name')
        context['priorities'] = Priority.objects.all().order_by('level')
        
        # Statistics
        context['total_tasks'] = Task.objects.count()
        context['completed_tasks'] = Task.objects.filter(status__is_completed=True).count()
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=datetime.now(),
            status__is_completed=False
        ).count()
        
        return context

    def post(self, request, *args, **kwargs):
        if 'add_task' in request.POST:
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save()
                messages.success(request, f'Task "{task.name}" created successfully!')
                return redirect('task_list')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['task_form'] = form
                return self.render_to_response(context)
        
        elif 'add_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                messages.success(request, f'Category "{category.name}" created successfully!')
                return redirect('task_list')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['category_form'] = form
                return self.render_to_response(context)
        
        elif 'add_member' in request.POST:
            form = MemberForm(request.POST)
            if form.is_valid():
                member = form.save()
                messages.success(request, f'Member "{member.name}" added successfully!')
                return redirect('task_list')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['assignee_form'] = form
                return self.render_to_response(context)
        
        elif 'add_status' in request.POST:
            form = StatusForm(request.POST)
            if form.is_valid():
                status = form.save()
                messages.success(request, f'Status "{status.name}" created successfully!')
                return redirect('task_list')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['status_form'] = form
                return self.render_to_response(context)
        
        elif 'add_priority' in request.POST:
            form = PriorityForm(request.POST)
            if form.is_valid():
                priority = form.save()
                messages.success(request, f'Priority "{priority.name}" created successfully!')
                return redirect('task_list')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['priority_form'] = form
                return self.render_to_response(context)
        
        return redirect('task_list')


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TaskCommentForm()
        context['comments'] = self.object.comments.all()
        return context


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_comment(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user.member if hasattr(request.user, 'member') else None
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('task_detail', pk=task_id)


@csrf_exempt
def update_task_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            status_id = data.get('status_id')
            
            task = get_object_or_404(Task, pk=task_id)
            status = get_object_or_404(Status, pk=status_id)
            
            old_status = task.status
            task.status = status
            task.save()
            
            # Mark as completed if status is completed
            if status.is_completed:
                task.mark_completed()
            
            return JsonResponse({
                'success': True,
                'message': f'Task "{task.name}" moved to {status.name}'
            })
            
        except (Task.DoesNotExist, Status.DoesNotExist):
            return JsonResponse({
                'success': False, 
                'error': 'Invalid task or status ID'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    }, status=405)


@login_required
def dashboard(request):
    """Dashboard view with statistics and charts"""
    context = {}
    
    # Task statistics
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status__is_completed=True).count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=datetime.now(),
        status__is_completed=False
    ).count()
    
    # Tasks by status
    status_counts = Status.objects.annotate(
        task_count=Count('tasks')
    ).order_by('order')
    
    # Tasks by priority
    priority_counts = Priority.objects.annotate(
        task_count=Count('tasks')
    ).order_by('level')
    
    # Recent tasks
    recent_tasks = Task.objects.select_related(
        'status', 'priority', 'assigned_to'
    ).order_by('-created_at')[:10]
    
    # Upcoming deadlines
    upcoming_deadlines = Task.objects.filter(
        due_date__gte=datetime.now(),
        due_date__lte=datetime.now() + timedelta(days=7),
        status__is_completed=False
    ).order_by('due_date')
    
    context.update({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'recent_tasks': recent_tasks,
        'upcoming_deadlines': upcoming_deadlines,
    })
    
    return render(request, 'dashboard.html', context)


@login_required
def bulk_actions(request):
    """Handle bulk actions on tasks"""
    if request.method == 'POST':
        action = request.POST.get('action')
        task_ids = request.POST.getlist('task_ids')
        
        if action and task_ids:
            tasks = Task.objects.filter(id__in=task_ids)
            
            if action == 'delete':
                tasks.delete()
                messages.success(request, f'{len(task_ids)} tasks deleted successfully!')
            elif action == 'archive':
                tasks.update(is_archived=True)
                messages.success(request, f'{len(task_ids)} tasks archived successfully!')
            elif action == 'change_status':
                status_id = request.POST.get('status_id')
                if status_id:
                    status = get_object_or_404(Status, id=status_id)
                    tasks.update(status=status)
                    messages.success(request, f'{len(task_ids)} tasks status updated successfully!')
            elif action == 'change_priority':
                priority_id = request.POST.get('priority_id')
                if priority_id:
                    priority = get_object_or_404(Priority, id=priority_id)
                    tasks.update(priority=priority)
                    messages.success(request, f'{len(task_ids)} tasks priority updated successfully!')
        
        return redirect('task_list')
    
    return redirect('task_list')