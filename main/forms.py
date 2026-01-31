from django import forms
from django.contrib.auth.models import User
from .models import Student


class StudentRegistrationForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(user__isnull=True).order_by('full_name'),
        label='Выберите ученика',
        empty_label='--- Выберите ---'
    )
    username = forms.CharField(max_length=150, label='Имя пользователя')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

        return cleaned_data

    def save(self):
        student = self.cleaned_data['student']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']

        # Создаём пользователя
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=student.full_name.split()[1] if len(student.full_name.split()) > 1 else '',
            last_name=student.full_name.split()[0] if len(student.full_name.split()) > 0 else ''
        )

        # Связываем с учеником
        student.user = user
        student.save()

        return user
