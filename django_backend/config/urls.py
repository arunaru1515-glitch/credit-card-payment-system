from django.contrib import admin
from django.urls import path, include

from accounts.views import (
    register_user,
    login_user,
    logout_user,
    protected_profile,
    add_card,
    list_cards,
    delete_card,
    block_card,
    unblock_card,
    update_credit_limit,
    list_audit_logs,
    list_users,
    update_user_role,
)
from transactions.views import system_health_metrics


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

    # RBAC - Card Block/Unblock
    path(
        'api/cards/<int:card_id>/block/',
        block_card,
        name='block-card'
    ),

    path(
        'api/cards/<int:card_id>/unblock/',
        unblock_card,
        name='unblock-card'
    ),

    # RBAC - Credit Limit Update
    path(
        'api/cards/<int:card_id>/limit/',
        update_credit_limit,
        name='update-credit-limit'
    ),

    # RBAC - Audit Logs
    path(
        'api/audit-logs/',
        list_audit_logs,
        name='audit-logs'
    ),

    # RBAC - User & Role Management
    path(
        'api/users/',
        list_users,
        name='list-users'
    ),

    path(
        'api/users/<int:user_id>/role/',
        update_user_role,
        name='update-user-role'
    ),

    # Module 4 - Transaction History
    path(
        'api/transactions/',
        include('transactions.urls')
    ),

    # System Monitoring & Health
    path(
        'api/system/health/',
        system_health_metrics,
        name='system-health-metrics'
    ),
]