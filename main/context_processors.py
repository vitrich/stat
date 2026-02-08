def user_badge(request):
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return {"user_badge": None}

    # По умолчанию
    badge = {
        "is_authenticated": True,
        "role": "Пользователь",
        "full_name": user.get_full_name() or user.username,
        "student_class": None,
    }

    # Если это учитель
    if hasattr(user, "teacherprofile"):
        t = user.teacherprofile
        badge["role"] = "Учитель"
        badge["full_name"] = getattr(t, "fullname", badge["full_name"])

    # Если это ученик
    elif hasattr(user, "student"):
        s = user.student
        badge["role"] = "Ученик"
        badge["full_name"] = getattr(s, "fullname", badge["full_name"])
        badge["student_class"] = getattr(s, "classname", None)

    return {"user_badge": badge}
