from django.urls import path

from .views import (
    TransactionHistoryView,
    create_pending_transaction,
    update_transaction_status,
    dashboard_summary,
    monthly_statement,
)


urlpatterns = [
    path(
        "",
        TransactionHistoryView.as_view(),
        name="transaction-history",
    ),

    path(
        "create/",
        create_pending_transaction,
        name="create-pending-transaction",
    ),

    path(
        "<int:transaction_id>/status/",
        update_transaction_status,
        name="update-transaction-status",
    ),

    path(
        "dashboard/summary/",
        dashboard_summary,
        name="dashboard-summary",
    ),

    path(
        "monthly-statement/",
        monthly_statement,
        name="monthly-statement",
    ),
]