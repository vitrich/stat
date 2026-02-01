from django.contrib import admin
from .models import Student, Group, Teacher, GroupHistory, Lesson, LessonTask


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email']
    search_fields = ['full_name', 'email']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher', 'get_student_count']
    list_filter = ['teacher']
    search_fields = ['number']

    def get_student_count(self, obj):
        return obj.students.count()

    get_student_count.short_description = 'Количество учеников'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'class_name', 'current_group', 'user']
    list_filter = ['current_group', 'class_name']
    search_fields = ['full_name', 'user__username']
    ordering = ['full_name']


@admin.register(GroupHistory)
class GroupHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'transfer_date', 'reason']
    list_filter = ['group', 'transfer_date']
    search_fields = ['student__full_name', 'reason']
    date_hierarchy = 'transfer_date'
    ordering = ['-transfer_date']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'subject', 'grade', 'is_active', 'get_tasks_count']
    list_filter = ['subject', 'grade', 'is_active', 'date']
    search_fields = ['title', 'subject']
    date_hierarchy = 'date'
    ordering = ['-date']

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    get_tasks_count.short_description = 'Заданий создано'


@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'score', 'correct_count', 'total_count', 'submitted_at']
    list_filter = ['lesson', 'score', 'submitted_at']
    search_fields = ['student__full_name', 'lesson__title']
    readonly_fields = ['tasks_data', 'answers', 'submitted_at']
    ordering = ['-submitted_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('lesson', 'student')
        }),
        ('Задания и ответы', {
            'fields': ('tasks_data', 'answers'),
            'classes': ('collapse',)
        }),
        ('Результаты', {
            'fields': ('score', 'correct_count', 'total_count', 'submitted_at')
        }),
    )
