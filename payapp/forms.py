from django import forms
from django.contrib.auth import get_user_model
from register.models import BankAccount
from payapp.models import Card, PaymentRequest
from webapps2024.utils.choices import CURRENCY_CHOICES

User = get_user_model()

class CustomBankNameWidget(forms.Select):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"})




class AddBankForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["bank_name", "account_number", "pin"]

        # add widgets
        widgets = {
            "bank_name": forms.Select(
                attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}
            ),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "eg. 011 2233 345"}
            ),
            "pin": forms.TextInput(attrs={"class": "form-control", "placeholder": "eg. 1234"}),
        }
    
    def clean_account_number(self):
        """
        A method to clean the account number field by validating its length and content.

        Returns:
            str: The cleaned account number if it meets the validation criteria.
        """
        account_number = self.cleaned_data["account_number"]
        if len(account_number) != 10 or not account_number.isdigit():
            raise forms.ValidationError("Account number must be a 10-digit number.")
        return account_number
    
    def clean_pin(self):
        """
        A method to clean the pin number field by validating its length and content.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            str: The cleaned pin number if it meets the validation criteria.
        
        Raises:
            forms.ValidationError: If the pin number is not a 4-digit number.
        """
        pin = self.cleaned_data["pin"]
        if len(pin) != 4 or not pin.isdigit():
            raise forms.ValidationError("Pin number must be a 4-digit number.")
        return pin


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['card_type',  'card_number', 'expiration_date', 'cvv']

        widgets = {
            # 'user': forms.Select(attrs={'class': 'form-control'}),
            "card_type": forms.Select(
                attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}
            ),
            "card_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "eg. 122 2233 345"}
            ),
            "cvv": forms.TextInput(attrs={"class": "form-control", "placeholder": "eg. 123"}
            ),
        }
       

    # validates  card number and cvv
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if len(card_number) != 10 or not card_number.isdigit():
            raise forms.ValidationError("Card number must be a 10-digit number."
        )
        return card_number
    
    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if len(cvv) != 3 or not cvv.isdigit():
            raise forms.ValidationError("CVV must be a 3-digit number.")
        return cvv



class DirectPaymentForm(forms.Form):
    amount = forms.DecimalField(
        label="Amount", required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount'}
    ))
    recipient_email = forms.EmailField(
        label="Recipient Email", required=False, widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Recipient Email'}
    ))
   
    senders_currency = forms.ChoiceField(
        label="Sender Currency", required=False, choices=CURRENCY_CHOICES.choices, 
        widget=forms.Select(attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}
    ))
    recipient_currency = forms.ChoiceField(
        label="Sender Currency", required=False, choices=CURRENCY_CHOICES.choices, 
        widget=forms.Select(attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}
    ))



class PaymentRequestForm(forms.ModelForm):
    recipient_email = forms.EmailField(label="Recipient Email", widget=forms.EmailInput(
        attrs={"class": "form-control", "placeholder": "Recipient Email"}
    ))
    amount = forms.DecimalField(label="Amount", widget=forms.NumberInput(
        attrs={"class": "form-control", "placeholder": "Amount"}
    ))
    message = forms.CharField(label="Message", required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Payment Description"}
    ))

    currency = forms.ChoiceField(label="Currency", choices=CURRENCY_CHOICES.choices,
      widget=forms.Select(attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}))

    class Meta:
        model = PaymentRequest
        fields = ["recipient_email", "amount", "message", "currency"]
        


class WithdrawalForm(forms.Form):
    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.none(),
                    widget=forms.Select(
                        attrs={"class": "custom-select", "id": "input-zon", "name": "zone_id"}                    
    ))
    amount = forms.DecimalField(min_value=0.01, 
                    widget=forms.NumberInput(
                        attrs={'class': 'form-control', 'placeholder': 'Enter amount'}
    ))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)
