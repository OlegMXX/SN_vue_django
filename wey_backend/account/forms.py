from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'password1', 'password2', 'avatar',)


class ProfileForm(ModelForm): # for profile edit
    class Meta:
        model = User
        fields = ('email', 'name', 'avatar',)