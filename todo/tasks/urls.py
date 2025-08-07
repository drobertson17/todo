from django.urls import path
from .views import TaskList, NewTask, NewCategory, NewMember, NewStatus

urlpatterns = [
    path("", TaskList.as_view(), name='task_list'),
    path("new-task/", NewTask.as_view(), name='new_task'),
    path("new-category/", NewCategory.as_view(), name='new_category'),
    path("new-assingee/", NewMember.as_view(), name='new_assignee'),
    path("new-status/", NewStatus.as_view(), name='new_status'),
]