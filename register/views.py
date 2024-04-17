from django.shortcuts import render, redirect
from register.forms import UserRegistrationForm, OnlineAccountForm
from register.models import OnlineAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from payapp.models import CurrencyConversion
from django.urls import reverse
from webapps2024.utils.manual_exchange import MANUAL_EXCHANGE_RATES
from django.http import HttpResponseRedirect
from django.contrib import messages


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



@login_required(login_url='/account/login')
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


def user_dashboard(request):
    return render(request, "register/user_dashboard.html")
