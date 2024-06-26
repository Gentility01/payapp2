from django.contrib import admin
from .models import Transaction, CurrencyConversion, TransactionHistory, Card, PaymentRequest

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'amount']
    search_fields = ['sender__username', 'recipient__username']
    list_filter = ['transaction_type']

    # def get_currency(self, obj):
    #     return obj.currency
    # get_currency.short_description = 'Currency'

@admin.register(CurrencyConversion)
class CurrencyConversionAdmin(admin.ModelAdmin):
    list_display = ['currency_from', 'currency_to', 'exchange_rate']

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'bank_account', 'amount', 'description', 'status']
    search_fields = ['sender__username', 'recipient__username', 'description']
    list_filter = ['status']

    # def get_acceptance_status(self, obj):
    #     if obj.status == 'Accepted':
    #         return 'Accepted'
    #     elif obj.status == 'Rejected':
    #         return 'Rejected'
    #     else:
    #         return 'Pending'

    # get_acceptance_status.short_description = 'Acceptance Status'

    def get_currency(self, obj):
        return obj.currency

admin.site.register(TransactionHistory, TransactionHistoryAdmin)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_number', 'expiration_date', 'cvv']

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'amount']
