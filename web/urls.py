"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная
    path('', views.home, name='home'),

    # Новости
    path('news/', views.news, name='news'),
    path('news/archive/', views.news_archive, name='news_archive'),

    # Задачи
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/active/', views.tasks_active, name='tasks_active'),
    path('tasks/completed/', views.tasks_completed, name='tasks_completed'),
    path('tasks/create/', views.tasks_create, name='tasks_create'),

    # Ученики
    path('students/', views.students, name='students'),
    path('students/list/', views.students_list, name='students_list'),
    path('students/groups/', views.students_groups, name='students_groups'),
    path('students/progress/', views.students_progress, name='students_progress'),

    # Статистика
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/overview/', views.stats_overview, name='stats_overview'),
    path('statistics/reports/', views.stats_reports, name='stats_reports'),
    path('statistics/analytics/', views.stats_analytics, name='stats_analytics'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('lesson/<str:lesson_date>/', views.lesson_view, name='lesson_view'),
    path('lesson/<str:lesson_date>/result/', views.lesson_result, name='lesson_result'),
]
