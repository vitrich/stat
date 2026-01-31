from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Teacher, Group, Student, GroupHistory, Assignment, Submission


# Расширяем стандартную админку User
class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Профиль преподавателя'


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Профиль ученика'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (TeacherInline, StudentInline)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role']

    def get_role(self, obj):
        if hasattr(obj, 'teacher_profile'):
            return '👨‍🏫 Преподаватель'
        elif hasattr(obj, 'student_profile'):
            return '👨‍🎓 Ученик'
        return '🔧 Админ'

    get_role.short_description = 'Роль'


# Перерегистрируем User с новой админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'user', 'get_groups_count']
    search_fields = ['full_name', 'email']
    list_filter = ['groups']

    def get_groups_count(self, obj):
        return obj.groups.count()

    get_groups_count.short_description = 'Кол-во групп'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher', 'get_students_count', 'color']
    list_filter = ['number', 'teacher']
    search_fields = ['description']

    def get_students_count(self, obj):
        return obj.students.count()

    get_students_count.short_description = 'Кол-во учеников'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'current_group', 'is_registered', 'user', 'parent_contact']
    list_filter = ['current_group', 'is_registered']
    search_fields = ['full_name', 'parent_contact']
    actions = ['mark_as_registered', 'mark_as_unregistered']

    def mark_as_registered(self, request, queryset):
        queryset.update(is_registered=True)

    mark_as_registered.short_description = "Отметить как зарегистрированных"

    def mark_as_unregistered(self, request, queryset):
        queryset.update(is_registered=False)

    mark_as_unregistered.short_description = "Отметить как незарегистрированных"


@admin.register(GroupHistory)
class GroupHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'transfer_date', 'reason']
    list_filter = ['group', 'transfer_date']
    search_fields = ['student__full_name', 'reason']
    date_hierarchy = 'transfer_date'
    ordering = ['-transfer_date']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'teacher', 'deadline', 'created_at', 'get_submissions_count']
    list_filter = ['group', 'teacher', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'

    def get_submissions_count(self, obj):
        return obj.submissions.count()

    get_submissions_count.short_description = 'Сдано работ'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'grade', 'submitted_at', 'has_file']
    list_filter = ['assignment__group', 'grade', 'submitted_at']
    search_fields = ['student__full_name', 'assignment__title']
    readonly_fields = ['submitted_at']
    date_hierarchy = 'submitted_at'

    def has_file(self, obj):
        return '✓' if obj.file else '✗'

    has_file.short_description = 'Файл'
    has_file.boolean = True


# Настройка заголовков админки
admin.site.site_header = '🧮 Math Letovo Junior - Администрирование'
admin.site.site_title = 'MLJ Admin'
admin.site.index_title = 'Управление системой'
