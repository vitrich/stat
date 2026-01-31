from django import forms
from django.contrib.auth.models import User
from .models import Student


class StudentRegistrationForm(forms.Form):
    """Форма регистрации ученика с выбором из базы"""
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_registered=False).order_by('full_name'),
        label='Выберите себя из списка',
        empty_label='-- Выберите своё имя --',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 12px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-primary); font-size: 15px;'
        })
    )

    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        help_text='Придумайте логин для входа',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: ivan_ivanov',
            'style': 'width: 100%; padding: 12px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-primary); font-size: 15px;'
        })
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте пароль',
            'style': 'width: 100%; padding: 12px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-primary); font-size: 15px;'
        })
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'style': 'width: 100%; padding: 12px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-primary); font-size: 15px;'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Это имя пользователя уже занято')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

        return cleaned_data

    def save(self):
        """Создаём пользователя и связываем с учеником"""
        student = self.cleaned_data['student']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']

        # Создаём пользователя
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=student.full_name.split()[0] if ' ' in student.full_name else student.full_name
        )

        # Связываем с учеником
        student.user = user
        student.is_registered = True
        student.save()

        return user
