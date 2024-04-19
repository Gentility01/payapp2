from django.urls import path
from register.views import (
    user_registration_page, online_account_setup, 
    user_login, user_logout, user_dashboard, administrator_create_view
)


urlpatterns = [
    path("register", user_registration_page, name="user_registration_page"),
    path("administrator_create_view", administrator_create_view, name="administrator_create_view"),
    path("online_account_setup", online_account_setup, name="online_account_views"),
    path("login", user_login, name="user_login"),
    path("logout", user_logout, name="user_logout"),
    path("dashboard", user_dashboard, name="user_dashboard"),
]
