from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from jsonschema import ValidationError
from .models import Product, Company, Vinil, CD, Accessory, Clothing

User = get_user_model()


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
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'address', 'phone', 'country')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 9:
            raise ValidationError("O número de telefone deve conter exatamente 9 dígitos.")
        return phone


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
        exclude = ['company']  # `company` will be set in the view

class VinilForm(forms.ModelForm):
    class Meta:
        model = Vinil
        fields = ['genre', 'lpSize', 'releaseDate', 'stock']

class CDForm(forms.ModelForm):
    class Meta:
        model = CD
        fields = ['genre', 'releaseDate', 'stock']

class ClothingForm(forms.ModelForm):
    class Meta:
        model = Clothing
        fields = ['color']

class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['material', 'color', 'size', 'stock']

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

