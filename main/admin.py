from django.contrib import admin
from .models import (
    Teacher, Group, Student, GroupHistory,
    Lesson, LessonTask,
    Assignment, Submission
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("fullname", "user", "email")
    search_fields = ("fullname", "email", "user__username")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("number", "teacher", "color")
    list_filter = ("number",)
    search_fields = ("number", "teacher__fullname")
    ordering = ("number",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("fullname", "classname", "currentgroup", "user")
    list_filter = ("currentgroup", "classname")
    search_fields = ("fullname", "classname", "user__username")
    ordering = ("fullname",)


@admin.register(GroupHistory)
class GroupHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "group", "transferdate", "reason")
    list_filter = ("group", "transferdate")
    date_hierarchy = "transferdate"
    search_fields = ("student__fullname", "group__number")
    ordering = ("-transferdate",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "grade", "subject", "isactive")
    list_filter = ("grade", "subject", "isactive")
    search_fields = ("title",)
    ordering = ("-date",)


@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    list_display = ("lesson", "student", "score", "correctcount", "totalcount", "submittedat")
    list_filter = ("lesson", "submittedat")
    search_fields = ("student__fullname", "lesson__title")
    ordering = ("-submittedat",)

    readonly_fields = ("tasksdata", "answers", "submittedat")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "teacher", "deadline", "createdat")
    list_filter = ("group", "teacher")
    search_fields = ("title", "group__number", "teacher__fullname")
    ordering = ("-createdat",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "submittedat", "grade")
    list_filter = ("grade", "submittedat")
    search_fields = ("assignment__title", "student__fullname")
    ordering = ("-submittedat",)
