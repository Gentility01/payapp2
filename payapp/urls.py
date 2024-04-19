from django.urls import path

from payapp import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("bank-account", views.backaccount, name="backaccount" ),
    path("add-bank", views.add_bank, name="add_bank"),
    path("addcard", views.addcard, name="addcard"),
    path("card-list", views.card_list, name="card_list"),
    path("deposite-money", views.deposite_money, name="deposite_money"),
    path("bank_selection", views.bank_selection, name="bank_selection"),
    path("bank_deposit_receipt/<int:pk>", views.bank_deposit_receipt, name="bank_deposit_receipt"),
    path("card_selection", views.card_selection, name="card_selection"),
    path("card_deposit_receipt/<int:pk>", views.card_deposit_receipt_view, name="card_deposit_receipt"),
    path("send_money", views.directpayment_or_send_money, name="directpayment_or_send_money"),
    path("directpayment_confirmation", views.directpayment_confirmation, name="directpayment_confirmation"),
    path("payment_success", views.payment_success, name="payment_success"),
    path("payment_failed", views.payment_failed, name="payment_failed"),
    path("transaction-history", views.all_reansaction_history, name="all_reansaction_history"),
    path("request_money", views.request_money, name="request_money"),
    path("payment_request_success", views.payment_request_success, name="payment_request_success"),
    path("respond_to_payment/<int:pk>/", views.respond_to_payment_request, name="respond_to_payment_request"),
    path("payment_request_list", views.payment_request_list_view, name="payment_request_list"),
    path("withdraw_money", views.withdrawal_view, name="withdrawal_view"),
    path("withdraw_money_confirm", views.withdraw_money_confirm, name="withdraw_money_confirm"),
    path("withdraw_success", views.withdraw_success, name="withdraw_success")
]
