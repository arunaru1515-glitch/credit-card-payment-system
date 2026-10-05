from django.contrib import admin
from django.urls import path, include

from accounts.views import (
    register_user,
    login_user,
    logout_user,
    protected_profile,
    add_card,
    list_cards,
    delete_card
)


urlpatterns = [

    # Admin
    path(
        'admin/',
        admin.site.urls
    ),

    # Module 1 - Registration
    path(
        'api/register/',
        register_user,
        name='register'
    ),

    # Module 1 - Login
    path(
        'api/login/',
        login_user,
        name='login'
    ),

    # Module 1 - Logout
    path(
        'api/logout/',
        logout_user,
        name='logout'
    ),

    # Module 1 - Protected Profile
    path(
        'api/profile/',
        protected_profile,
        name='profile'
    ),

    # Module 2 - Add Card
    path(
        'api/cards/',
        add_card,
        name='add-card'
    ),

    # Module 2 - View Saved Cards
    path(
        'api/cards/list/',
        list_cards,
        name='list-cards'
    ),

    # Module 2 - Delete Card
    path(
        'api/cards/<int:card_id>/',
        delete_card,
        name='delete-card'
    ),

    # Module 4 - Transaction History
    path(
        'api/transactions/',
        include('transactions.urls')
    ),
]