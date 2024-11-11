from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from jsonschema import ValidationError
from .models import Product, Company, Vinil, CD, Accessory, Clothing

User = get_user_model()


from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator
from .models import User


from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, help_text='Required. Inform a valid email address.')
    password1 = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=50, required=True)
    country = forms.CharField(max_length=50, required=True)
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2', 
            'first_name', 'last_name', 'address', 'phone', 'country', 'image'
        )

    def validate_invisible_characters(self, value):
        # Remove espaços e caracteres invisíveis (zero-width spaces, tabs, etc.)
        value = re.sub(r'\s+|\u200B|\u200C|\u200D|\u2060', '', value)
        if not value:
            raise ValidationError("O campo não pode conter apenas caracteres invisíveis.")
        return value

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        username = self.validate_invisible_characters(username)
        if len(username) < 3 and len(username) < 9:
            raise ValidationError("O campo 'Username' deve ter pelo menos 3 caracteres.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este username já está em uso.")
        return username

    def clean_email(self) :
        email = self.cleaned_data.get('email', '').strip()
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError("O campo 'Email' deve conter um endereço de email válido.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email já está em uso.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        first_name = self.validate_invisible_characters(first_name)
        if len(first_name) < 2 and len(first_name) < 9:
            raise ValidationError("O campo 'First Name' deve ter pelo menos 2 caracteres.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        last_name = self.validate_invisible_characters(last_name)
        if len(last_name) < 2 and len(last_name) < 9 :
            raise ValidationError("O campo 'Last Name' deve ter pelo menos 2 caracteres.")
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit():
            raise ValidationError("O número de telefone deve conter apenas dígitos.")
        if len(phone) != 9:
            raise ValidationError("O número de telefone deve conter exatamente 9 dígitos.")
        return phone

    def clean_country(self):
        country = self.cleaned_data.get('country', '').strip()
        country = self.validate_invisible_characters(country)
        if len(country) < 2  and len(country) < 9:
            raise ValidationError("O campo 'Country' deve ter pelo menos 2 caracteres.")
        return country

    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()
        if address:
            address = self.validate_invisible_characters(address)
            if len(address) < 5 and len(address) < 20:
                raise ValidationError("O campo 'Address' deve ter pelo menos 5 caracteres.")
        return address

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("As senhas não coincidem.")
        if len(password1) < 8:
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return password2

class UploadUserProfilePicture(forms.Form):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 
                                                           'id': 'image',
                                                             'name': 'image',
                                                             'accept': 'image/*'}))
    

class UpdatePassword(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Senha Antiga")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nova Senha")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Nova Senha")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("As senhas não coincidem.")
    

class UpdateProfile(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, help_text='Required. Inform a valid email address.')
    address = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=50, required=False)
    country = forms.CharField(max_length=50, required=False)
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 
                                                           'id': 'image',
                                                             'name': 'image',
                                                             'accept': 'image/*'}))
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")
        country = cleaned_data.get("country")

        if email and phone and country:
            raise forms.ValidationError("Preencha pelo menos um campo.")
        

class ProductForm(forms.ModelForm):
    PRODUCT_TYPE_CHOICES = [
        ('vinil', 'Vinil'),
        ('cd', 'CD'),
        ('clothing', 'Clothing'),
        ('accessory', 'Accessory'),
    ]
    product_type = forms.ChoiceField(choices=PRODUCT_TYPE_CHOICES, required=True, label="Product Type")

    class Meta:
        model = Product
        fields = ['product_type', 'name', 'description', 'price', 'image', 'artist', 'category']
        widgets = {
            'category': forms.HiddenInput(),  # This makes 'category' hidden since it's set by JS
        }

class VinilForm(forms.ModelForm):
    class Meta:
        model = Vinil
        fields = ['genre', 'lpSize', 'releaseDate', 'stock']
        widgets = {
            'genre': forms.TextInput(attrs={'required': False}),
            'lpSize': forms.NumberInput(attrs={'required': False}),
            'releaseDate': forms.DateInput(attrs={'type': 'date', 'required': False}),
            'stock': forms.NumberInput(attrs={'required': False}),
        }

class CDForm(forms.ModelForm):
    class Meta:
        model = CD
        fields = ['genre', 'releaseDate', 'stock']
        widgets = {
            'genre': forms.TextInput(attrs={'required': False}),
            'releaseDate': forms.DateInput(attrs={'type': 'date', 'required': False}),
            'stock': forms.NumberInput(attrs={'required': False}),
        }

class ClothingForm(forms.ModelForm):
    class Meta:
        model = Clothing
        fields = ['color']
        widgets = {
            'color': forms.TextInput(attrs={'required': False}),
        }

class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['material', 'color', 'size', 'stock']
        widgets = {
            'material': forms.TextInput(attrs={'required': False}),
            'color': forms.TextInput(attrs={'required': False}),
            'size': forms.NumberInput(attrs={'required': False}),
            'stock': forms.NumberInput(attrs={'required': False}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'email', 'phone', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ['username', 'country', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class ReviewForm(forms.Form):
    rating = forms.IntegerField(required=False)
    review = forms.CharField(required=False, widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        review = cleaned_data.get('review', '').strip()

        if not rating and not review:
            raise forms.ValidationError("Por favor, forneça uma avaliação com estrelas ou escreva um texto.")
        return cleaned_data