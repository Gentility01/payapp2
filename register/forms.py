from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, OnlineAccount
from  webapps2024.utils.choices import CURRENCY_CHOICES

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data["full_name"]
        first_name, last_name = full_name.split(" ", 1)
        user.first_name = first_name
        user.last_name = last_name
        user.username = first_name.lower()  # Set username as lowercase first name
        if commit:
            user.save()
        return user


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({
             'placeholder': 'John Doe'
        })
        
        self.fields['email'].widget.attrs.update({
            'placeholder': 'example@gmail.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Confirm Password'
        })


class OnlineAccountForm(forms.ModelForm):
    class Meta:
        model = OnlineAccount
        fields = ['currency']
        widgets = {
            'currency': forms.Select(
                attrs={'class': 'form-select', 'required': 'required'}, choices=CURRENCY_CHOICES
            ),
        }
    
    