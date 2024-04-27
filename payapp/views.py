from django.shortcuts import render, redirect, get_object_or_404
from register.models import BankAccount, OnlineAccount
from payapp.models import TransactionHistory, PaymentRequest, Card, Transaction
from django.contrib.auth.decorators import login_required

from payapp.forms import AddBankForm, CardForm, DirectPaymentForm, PaymentRequestForm, WithdrawalForm
from django.urls import reverse, reverse_lazy
from decimal import Decimal
from register.models import CustomUser
from django.db import transaction
from django.contrib import messages
from webapps2024.utils.manual_exchange import MANUAL_EXCHANGE_RATES
# Create your views here.






def homepage(request):
    return render(request, "payapp/homepage.html")


@login_required(login_url=reverse_lazy("user_login"))
def backaccount(request):
    """
    Renders the 'bankaccount.html' template with the list of BankAccount objects.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'bankaccount.html' template with the list of bank accounts.
    """

    banks = BankAccount.objects.filter(user=request.user)

    context = {
        "banks":banks
    }
    return render(request, "payapp/bankaccount.html", context)

@login_required(login_url=reverse_lazy("user_login"))
def add_bank(request):
    """
    Adds a new bank account for the logged-in user.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'addbank.html' template with the AddBankForm if the request method is GET.
                      Redirects to 'backaccount' if the form is valid and the request method is POST.
    """
    if request.method == "POST":
        form = AddBankForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.user = request.user
            bank_account.save()
            return redirect("backaccount")
    else:
        form = AddBankForm()
    return render(request, "payapp/addbank.html", {"form": form})



@login_required(login_url=reverse_lazy("user_login"))
def addcard(request):
    """
    View function for adding a new card.

    This function is used to handle the HTTP POST request for adding a new card. It requires the user to be authenticated, otherwise it redirects to the login page. The function takes in a request object and returns an HTTP response.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'addcard.html' template with the CardForm if the request method is GET. 
                      Redirects to 'card_list' if the form is valid and the request method is POST.
    """
    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect("card_list")
    else:
        form = CardForm()
    return render(request, "payapp/addcard.html", {"form": form})

@login_required(login_url=reverse_lazy("user_login"))
def card_list(request):
    """
    Renders the 'payapp/cardlist.html' template and returns an HttpResponse.
    
    This function is a view that is used to display the list of cards for the logged-in user. It requires the user to be authenticated, otherwise it redirects them to the login page.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: The rendered 'payapp/cardlist.html' template.
    """
    return render(request, "payapp/cardlist.html")



@login_required(login_url=reverse_lazy("user_login"))
def deposite_money(request):
    """
    View function for depositing money.

    This function is used to handle the HTTP POST request for depositing money. It requires the user to be authenticated, otherwise it redirects to the login page. The function takes in a request object and returns an HTTP response.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'payapp/deposite.html' template if the request method is GET. 
                      Redirects to 'bank_selection' if the payment method is 'Bank Account', 
                      redirects to 'card_selection' if the payment method is 'Credit or Debit Cards', 
                      or redirects back to 'deposite_money' if the payment method is neither 'Bank Account' nor 'Credit or Debit Cards'.
    """
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        amount = request.POST.get("amount")
       
        if payment_method == "Bank Account":
            return redirect(reverse("bank_selection") + f"?amount={amount}")
        elif payment_method == "Credit or Debit Cards":
            return redirect(reverse("card_selection") + f"?amount={amount}")
        else:
            return redirect(reverse('deposite_money'))
    return render(request, "payapp/deposite.html")




@login_required(login_url=reverse_lazy("user_login"))
def bank_selection(request):
    """
    A decorator that ensures the user is logged in before accessing the bank_selection function.
    If the request method is GET, it retrieves the amount and bank accounts for the user and renders the bank_selection.html template.
    If the request method is POST, it processes the bank deposit, updates the user's online account balance, records the transaction history, and redirects to the bank deposit receipt page.
    """
    if request.method == 'GET':
        amount = request.GET.get('amount', '')
        bank_accounts = BankAccount.objects.filter(user=request.user)
        return render(request, "payapp/bank_selection.html", {'amount': amount, 'bank_accounts': bank_accounts})

    if request.method == 'POST':
        bank_account_id = request.POST.get("bank_account")
        amount = Decimal(request.POST.get("amount"))  # Convert amount to Decimal
        bank_account = get_object_or_404(BankAccount, id=bank_account_id, user=request.user)

        # Update user's online account balance
        online_account = OnlineAccount.objects.get(user=request.user)
        online_account.balance += amount  # Add amount directly (now it's a Decimal)
        online_account.save()

        # Record transaction history
        TransactionHistory.objects.create(
            sender=request.user,
            description='Deposit from bank account',
            status='✔️',
            amount=amount,
            bank_account=bank_account
        )

        # Redirect to bank deposit receipt page
        return redirect(reverse('bank_deposit_receipt', kwargs={'pk': bank_account_id}) + f'?amount={amount}')

 
 
@login_required(login_url=reverse_lazy("user_login"))
def bank_deposit_receipt(request, pk):
    """
	A decorator that ensures the user is logged in before accessing the bank_deposit_receipt function.
	It retrieves the bank account information based on the primary key 'pk' and user.
	Renders the 'payapp/bank_deposit_receipt.html' template with bank account and amount data.
	"""
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    amount = request.GET.get('amount', '')

    return render(request, 'payapp/bank_deposit_receipt.html', {'bank_account': bank_account, 'amount': amount})





@login_required(login_url=reverse_lazy("user_login"))
def card_selection(request):
    """
    View function for handling the card selection page.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - If the request method is GET, it renders the "card_selection.html" template with the amount and cards as context variables.
    - If the request method is POST, it performs the following actions:
        - Retrieves the selected card ID and amount from the request.
        - Retrieves the selected card object for the current user.
        - Updates the online account balance of the current user by adding the specified amount.
        - Creates a new transaction history record for the deposit from card.
        - Redirects to the "card_deposit_receipt" page with the card ID and amount as parameters.
    """
    if request.method == 'GET':
        amount = request.GET.get('amount', '')
        cards = Card.objects.filter(user=request.user)
        return render(request, "payapp/card_selection.html", {'amount': amount, 'cards': cards})

    if request.method == 'POST':
        card_id = request.POST.get("card")
        amount = Decimal(request.POST.get("amount"))  # Convert amount to Decimal
        card = get_object_or_404(Card, id=card_id, user=request.user)

        # Update user's online account balance
        online_account = OnlineAccount.objects.get(user=request.user)
        online_account.balance += amount  # Add amount directly (now it's a Decimal)
        online_account.save()

        # Record transaction history
        TransactionHistory.objects.create(
            sender=request.user,
            description='Deposit from card',
            status='✔️',
            amount=amount,
            # card=card
        )
        
        return redirect(reverse('card_deposit_receipt', kwargs={'pk': card_id}) + f'?amount={amount}')



@login_required(login_url=reverse_lazy("user_login"))
def card_deposit_receipt_view(request, pk):
    """
    A view function for displaying the card deposit receipt.
    
    Parameters:
    - request: The HTTP request object.
    - pk: The primary key of the card to display.

    Returns:
    - Renders the 'payapp/card_deposit_receipt.html' template with card and amount as context variables.
    """
    card = get_object_or_404(Card, id=pk, user=request.user)
    amount = request.GET.get('amount', '')

    return render(request, 'payapp/card_deposit_receipt.html', {'card': card, 'amount': amount})



@login_required(login_url=reverse_lazy("user_login"))
def directpayment_or_send_money(request):
    """
    This function handles the direct payment or send money process. It requires the user to be logged in, otherwise it redirects to the user login page.
    
    Parameters:
    - request: The HTTP request object.
    
    Returns:
    - If the request method is POST, it validates the DirectPaymentForm and if valid, stores the form data in the session for the next page. It then redirects to the "directpayment_confirmation" page.
    - If the form is not valid, it displays an error message and renders the 'payapp/direct_payment_form.html' template with the form as context.
    - If the request method is not POST, it renders the 'payapp/directpayment_or_send_money.html' template with an empty DirectPaymentForm as context.
    """
    if request.method == "POST":
        form = DirectPaymentForm(request.POST)
        if form.is_valid():
            # Retrieve form data
            payment_data = form.cleaned_data
            # Ensure currency is added to payment_data
            payment_data['currency'] = 'USD'  # Replace 'USD' with the default currency or fetch it from the form
            # Convert decimal objects to string
            payment_data['amount'] = str(payment_data['amount'])
            # Store data in session
            request.session['payment_data'] = payment_data
            # Redirect to confirmation page
            return redirect("directpayment_confirmation")
        else:
            # Form is not valid, display errors
            messages.error(request, "Please correct the errors below.")
            return render(request, 'payapp/direct_payment_form.html', {'form': form})
    else:
        # Render form for user input
        form = DirectPaymentForm()
        return render(request, "payapp/directpayment_or_send_money.html", {'form': form})

@login_required(login_url=reverse_lazy("user_login"))
def directpayment_confirmation(request):
    payment_data = request.session.get('payment_data', {})
    recipient_email = payment_data.get('recipient_email')

    try:
        # Get the recipient user by email
        recipient = CustomUser.objects.get(email=recipient_email)
    except CustomUser.DoesNotExist:
        recipient = None

    context = {'payment_data': payment_data, 'recipient': recipient}

    if recipient is None:
        context['recipient_not_found'] = True
        context['error_message'] = "Recipient user not found."
        return render(request, 'payapp/direct_payment_confirmation.html', context)

    if request.method == 'POST':
        form = DirectPaymentForm(request.POST)
        if form.is_valid():
            sender = request.user
            amount = payment_data.get('amount')
            currency = payment_data.get('currency')

            # Check if the recipient email is the same as the sender's email
            if sender.email == recipient_email:
                messages.error(request, "You cannot send a payment request to yourself.")
                return redirect('payment_failed')

            # Check if the sender has enough funds in their account
            sender_account = sender.onlineaccount
            if sender_account.balance < float(amount):
                # Sender doesn't have enough funds
                messages.error(request, "Insufficient funds.")
                return redirect('payment_failed')

            # Check if currency conversion is needed
            if sender_account.currency != recipient.onlineaccount.currency:
                # Currency conversion needed
                exchange_rate = MANUAL_EXCHANGE_RATES.get((sender_account.currency, recipient.onlineaccount.currency))
                if exchange_rate is None:
                    messages.error(request, "Exchange rate not found for currencies.")
                    return redirect('payment_failed')
                amount = float(amount)
                amount *= exchange_rate

            # Deduct the amount from the sender's account and add it to the recipient's account within a single transaction
            with transaction.atomic():
                sender_account.balance -= int(amount)
                sender_account.save()
                recipient_account = recipient.onlineaccount
                recipient_account.balance += int(amount)
                recipient_account.save()

                # Create a transaction record for the payment
                Transaction.objects.create(sender=sender, recipient=recipient, amount=amount, currency=currency, transaction_type="direct_payment")

                # Create transaction history records for both sender and recipient
                TransactionHistory.objects.create(sender=sender, recipient=recipient, status="✔️", amount=amount, description="Direct payment (sent)")
                TransactionHistory.objects.create(sender=recipient, recipient=sender, status="📥", amount=amount, description="Direct payment (received)")

            # Clear session data
            request.session.pop('payment_data', None)

            return redirect('payment_success')
        else:
            messages.error(request, "Please correct the errors below.")
            context['form'] = form
            return render(request, 'payapp/direct_payment_confirmation.html', context)
    else:
        form = DirectPaymentForm()
        context['form'] = form
    return render(request, 'payapp/directpayment_confirmation.html', context)


@login_required(login_url=reverse_lazy('register:login_view'))
def payment_success(request):
    payment_data = request.session.get('payment_data', {})
    return render(request, "payapp/payment_success.html", {'payment_data': payment_data})
    
@login_required(login_url=reverse_lazy('register:login_view'))
def payment_failed(request):
    return render(request, "payapp/payment_failed.html")


@login_required(login_url=reverse_lazy('register:login_view'))
def all_reansaction_history(request):
    return render(request, "payapp/all_transactionhistory.html")


@login_required(login_url=reverse_lazy('register:login_view'))
def request_money(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data["recipient_email"]
            try:
                recipient = CustomUser.objects.get(email=recipient_email)
            except CustomUser.DoesNotExist:
                messages.error(request, "Recipient user not found!")
                return redirect("payment_failed")

            if recipient == request.user:
                messages.error(request, "You cannot send a payment request to yourself!")
                return redirect("payment_failed")

            form.instance.sender = request.user
            form.instance.recipient = recipient
            form.instance.status = "pending"
            amount = form.cleaned_data["amount"]

            # Save the form to the database
            payment_request = form.save()

            # Create transaction history records for both sender and recipient
            TransactionHistory.objects.create(sender=request.user, recipient=recipient, status="✔️", amount=amount, description="Request Payment (sent)")
            TransactionHistory.objects.create(sender=recipient, recipient=request.user, status="📥", amount=amount, description="Request Payment (received)")

            messages.success(request, "Payment request sent successfully!")
            return redirect("payment_request_success")
    else:
        form = PaymentRequestForm()
    return render(request, "payapp/request_money.html", {"form": form})


@login_required(login_url=reverse_lazy('register:login_view'))
def payment_request_success(request):
    return render(request, "payapp/payment_request_success.html")



@login_required(login_url=reverse_lazy('register:login_view'))
def payment_request_list_view(request):

    payment_requests = PaymentRequest.objects.filter(recipient=request.user).order_by('-created_at')

    return render(request, "payapp/payment_request_list.html", {"payment_requests": payment_requests})





@transaction.atomic
@login_required(login_url=reverse_lazy('register:login_view'))
def respond_to_payment_request(request, pk):
    try:
        payment_request = PaymentRequest.objects.get(pk=pk)
    except PaymentRequest.DoesNotExist:
        messages.error(request, 'Payment request not found!')
        return redirect('payment_failed')

    if request.method == 'POST':
        action = request.POST.get('action')
        print("action", action, )
        if action == 'accepted':
            try:
                sender_account = OnlineAccount.objects.get(user=payment_request.sender)
                recipient_account = OnlineAccount.objects.get(user=payment_request.recipient)

                if recipient_account.balance >= payment_request.amount:
                    sender_account.balance += payment_request.amount
                    recipient_account.balance -= payment_request.amount
                    sender_account.save()
                    recipient_account.save()
                    #---------------------------
                    payment_request.status = 'SUCCESS'  # Update status to SUCCESS
                    payment_request.save()  # Save the updated status
                    #---------------------------
                    messages.success(request, 'Payment request accepted!')
                    TransactionHistory.objects.create(sender=payment_request.sender, recipient=payment_request.recipient, 
                    status="✔️", amount=payment_request.amount, description="Payment Request Accepted")
                    TransactionHistory.objects.create(sender=payment_request.recipient, recipient=payment_request.sender, 
                    status="📥", amount=payment_request.amount, description="Payment Request Accepted" )
                else:
                    messages.error(request, 'Insufficient balance to fulfill the payment request.')
                    return redirect('payment_failed')
            except OnlineAccount.DoesNotExist:
                messages.error(request, 'One of the accounts does not exist.')
        elif action == 'rejected':
            #---------------------------
            payment_request.status = 'FAILED'  # Update status to FAILED
            payment_request.save()  # Save the updated status
            #---------------------------
            messages.info(request, 'Payment request rejected!')
        else:
            messages.error(request, 'Invalid action.')

        return redirect('payment_request_list')

    return render(request, 'respond_to_payment_request.html', {'payment_request': payment_request})





@login_required(login_url=reverse_lazy('register:login_view'))
def withdrawal_view(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            # Store withdrawal details in session variables
            bank_account_id = form.cleaned_data['bank_account'].id
            amount = float(form.cleaned_data['amount'])  # Convert Decimal to float
            request.session['withdrawal_details'] = {
                'bank_account_id': bank_account_id,
                'amount': amount,
            }
            return redirect('withdraw_money_confirm')
    else:
        form = WithdrawalForm(user=request.user)
    return render(request, 'payapp/withdraw_money.html', {'form': form})


def withdraw_money_confirm(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            bank_account = form.cleaned_data['bank_account']
            amount = form.cleaned_data['amount']
            online_account = OnlineAccount.objects.get(user=request.user)
            if online_account.balance >= amount:
                online_account.balance -= amount
                online_account.save()

                # Record the transaction history
                TransactionHistory.objects.create(
                    sender=request.user, description='Withdrawal to bank account',
                    status='✔️', amount=amount, bank_account=bank_account)

                del request.session['withdrawal_details']
                messages.success(request, 'Withdrawal successful')
                return redirect('withdraw_success')
            else:
                messages.warning(request, 'Insufficient balance')
    else:
        withdrawal_details = request.session.get('withdrawal_details')
        if withdrawal_details:
            bank_account_id = withdrawal_details['bank_account_id']
            bank_account = BankAccount.objects.get(pk=bank_account_id)
            form_data = {
                'bank_account': bank_account,
                'amount': withdrawal_details['amount'],
            }
            form = WithdrawalForm(user=request.user, initial=form_data)
            for field in form.fields.values():
                field.widget.attrs['disabled'] = True
        else:
            messages.error(request, 'Withdrawal details not found')
            form = WithdrawalForm(user=request.user)

    return render(request, 'payapp/withdraw_confirm.html', {'form': form, 'bank_account': bank_account})

def withdraw_success(request):
    return render(request, "payapp/withdraw_success.html")