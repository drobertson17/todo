from django.urls import path
from .views import (
    TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete,
    update_task_status, add_comment, dashboard, bulk_actions
)

urlpatterns = [
    path("", TaskList.as_view(), name='task_list'),
    path('dashboard/', dashboard, name='dashboard'),
    path('task/new/', TaskCreate.as_view(), name='task_create'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task_detail'),
    path('task/<int:pk>/edit/', TaskUpdate.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', TaskDelete.as_view(), name='task_delete'),
    path('task/<int:task_id>/comment/', add_comment, name='add_comment'),
    path('update-task-status/', update_task_status, name='update_task_status'),
    path('bulk-actions/', bulk_actions, name='bulk_actions'),
]