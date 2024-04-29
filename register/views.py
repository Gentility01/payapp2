from django.shortcuts import render, redirect
from register.forms import UserRegistrationForm, OnlineAccountForm, AdministratorCreationForm
from register.models import OnlineAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from payapp.models import CurrencyConversion
from django.urls import reverse
from webapps2024.utils.manual_exchange import MANUAL_EXCHANGE_RATES
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy

from rest_framework.views import APIView
from rest_framework import status
from .serializers import CurrencyConversionSerializer
from rest_framework.response import Response
from decimal import Decimal


# Create your views here.\

def user_registration_page(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.email = form.cleaned_data["email"]
            user.save()

            # login in user authomatically
            login(request, user)
            request.session["user_id"] = user.id

            return redirect(reverse('online_account_views'))  # Success URL

    else:
        form = UserRegistrationForm()

    # Adding widget data to the context
    context = {
        'form': form,
        # 'currency_choices': CURRENCY_CHOICES,
    }
    return render(request, "register/user_registration.html", context)


def administrator_create_view(request):
    if request.method == 'POST':
        form = AdministratorCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            login(request, user)  # Log in the user immediately after registration
            return redirect('admin:index')
    else:
        form = AdministratorCreationForm()
    return render(request, 'register/admin_register.html', {'form': form})



@login_required(login_url=reverse_lazy("user_login"))
def online_account_setup(request):
    
    # Process the form
    if request.method == "POST":
        form = OnlineAccountForm(request.POST)  # Instantiate the form with request data
        if form.is_valid():
            # Retrieve the logged-in user
            user = request.user

            # Fetch the appropriate exchange rate for the selected currency
            selected_currency = form.cleaned_data['currency']
            try:
                # Fetch the CurrencyConversion object for the selected currency
                conversion_rate = CurrencyConversion.objects.get(currency_to=selected_currency)

                # Calculate the initial amount based on the baseline amount and exchange rate
                baseline_amount = 1000  
                initial_amount = baseline_amount * conversion_rate.exchange_rate
            except CurrencyConversion.DoesNotExist:
                # Handle the case where conversion rate for the selected currency doesn't exist
                manual_exchange_rate = MANUAL_EXCHANGE_RATES.get(("USD", selected_currency))
                if manual_exchange_rate is not None:
                    # Calculate the initial amount using the manual exchange rate
                    baseline_amount = 1000  
                    initial_amount = baseline_amount * manual_exchange_rate
                else:
                    # Handle the case where neither automatic nor manual conversion rates are available
                    error_message = "Conversion rate for the selected currency is not available."
                    return redirect("online_account_views")

            # Create or update the OnlineAccount for the user
            online_account, created = OnlineAccount.objects.get_or_create(user=user)
            online_account.currency = selected_currency
            online_account.balance = initial_amount
            online_account.save()

             # Redirect to the success URL
            return HttpResponseRedirect('/')
    else:
        # If the request method is GET, render the form
        form = OnlineAccountForm()

    return render(request, 'register/online_account_setup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('user_dashboard')
        else:
            # Return an 'invalid login' error message.
            messages.error(request, "Invalid email or password.")
            return redirect('user_login')
    return render(request, "register/user_login.html")


def user_logout(request):
    """
    Function-based view for user logout.
    """
    if request.method == 'POST':
        logout(request)
        return redirect('/')
    else:
        return render(request, "register/logout.html")

@login_required(login_url=reverse_lazy("user_login"))
def user_dashboard(request):
    return render(request, "register/user_dashboard.html")





class ConvertCurrencyAPIView(APIView):
    def get(self, request, currency1, currency2, amount_of_currency1):
        serializer = CurrencyConversionSerializer(data={'currency_from': currency1, 'currency_to': currency2, 'amount_of_currency_from': amount_of_currency1})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        currency_from = serializer.validated_data['currency_from']
        currency_to = serializer.validated_data['currency_to']
        amount_of_currency_from = Decimal(serializer.validated_data['amount_of_currency_from'])  # Convert to Decimal
        
        if (currency_from, currency_to) in MANUAL_EXCHANGE_RATES:
            exchange_rate = Decimal(MANUAL_EXCHANGE_RATES[(currency_from, currency_to)])  # Convert to Decimal
            converted_amount = amount_of_currency_from * exchange_rate
            return Response({'conversion_rate': exchange_rate, 'converted_amount': converted_amount}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'One or both currencies not supported'}, status=status.HTTP_400_BAD_REQUEST)



def error_404(request, exception):
    return render(request, 'register/404.html', status=404)
