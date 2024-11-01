from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UploadUserProfilePicture(forms.Form):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 
                                                           'id': 'image',
                                                             'name': 'image',
                                                             'accept': 'image/*'}))

