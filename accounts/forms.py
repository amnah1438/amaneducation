from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'اسم المستخدم',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'كلمة المرور',
        })
    )