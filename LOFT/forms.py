from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import ContactMessage, Customer, Shipping
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }), label='E-mail')

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }), label='Пароль')


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'off'
    }), label='Имя')

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'off'
    }), label='Фамилия')

    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'off'
    }), label='E-mail')

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'off'
    }), label='Номер телефона')

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'new-password'
    }), label='Пароль')

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input',
        'autocomplete': 'new-password'
    }), label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']



class EditUserForm(forms.ModelForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }), label='E-mail')
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Имя')
    
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Фамилия')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        

class EditCustomerForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TelInput(attrs={
        'class': 'contact__section-input'
    }), label='Номер телефона')
    
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Город')
    
    street = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Улица')
    
    home = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Дом/Корпус', required=False)
    
    flat = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Квартира', required=False)
    
    class Meta:
        model = Customer
        fields = ['phone', 'city', 'street', 'home', 'flat']

    
class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }), label='Имя')

    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }), label='E-mail')

    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'contact__section-input',
    }), label='Сообщение')
    
    file = forms.FileField(
    widget=forms.ClearableFileInput(attrs={'class': "btn btns__loadfile"}),
    label='Прикрепить файл',
    required=False
)
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'username', 'message', 'file']
        

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        fields = ('region', 'city', 'street', 'home', 'flat', 'phone', 'comment')
        widgets = {
            'region': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'home': forms.TextInput(attrs={'class': 'form-control'}),
            'flat': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TelInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'})
        }

