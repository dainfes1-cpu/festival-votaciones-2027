from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Ingresa un correo válido.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # 👇 NUEVA VALIDACIÓN
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado en el sistema.")
        return email