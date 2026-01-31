from django.contrib import admin
from .models import Student, Group, Teacher, GroupHistory


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
