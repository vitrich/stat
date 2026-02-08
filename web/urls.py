from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as authviews

from main import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('news/', views.news, name='news'),
    path('news/archive/', views.newsarchive, name='news_archive'),

    path('login/', authviews.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', authviews.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('lesson/<str:lessondate>/', views.lessonview, name='lessonview'),
    path('lesson/<str:lessondate>/result/', views.lessonresult, name='lessonresult'),

    path('tasks/', views.tasks, name='tasks'),
    path('tasks/active/', views.tasksactive, name='tasks_active'),
    path('tasks/completed/', views.taskscompleted, name='tasks_completed'),
    path('tasks/create/', views.taskscreate, name='tasks_create'),

    path('students/', views.students, name='students'),
    path('students/list/', views.studentslist, name='students_list'),
    path('students/groups/', views.studentsgroups, name='students_groups'),
    path('students/progress/', views.studentsprogress, name='students_progress'),

    path('statistics/', views.statistics, name='statistics'),
    path('statistics/overview/', views.statsoverview, name='stats_overview'),
    path('statistics/reports/', views.statsreports, name='stats_reports'),
    path('statistics/analytics/', views.statsanalytics, name='stats_analytics'),
]
