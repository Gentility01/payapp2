from django.contrib import admin
from .models import CustomUser, OnlineAccount, Administrator, UserProfile, BankAccount

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_currency']
    search_fields = ['username', 'email']

    def get_currency(self, obj):
        return obj.onlineaccount.currency
    get_currency.short_description = 'Currency'


@admin.register(OnlineAccount)
class OnlineAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'balance']
    search_fields = ['user__username']


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ['username']
    search_fields = ['user__username']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'payapp_account', 'address', 'phone_number', 'profile_picture']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank_name', 'account_number', 'pin']
