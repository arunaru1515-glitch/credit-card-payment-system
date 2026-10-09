from django.urls import path

from .views import (
    TransactionHistoryView,
    create_pending_transaction,
    update_transaction_status,
    dashboard_summary,
    monthly_statement,
    card_usage_analytics,
    export_analytics_csv,
    export_analytics_pdf,
    export_transactions_csv_api,
    list_fraud_logs,
    review_fraud_log,
)


urlpatterns = [
    # Transaction History (with advanced search & pagination)
    path(
        "",
        TransactionHistoryView.as_view(),
        name="transaction-history",
    ),

    # Create Pending Transaction
    path(
        "create/",
        create_pending_transaction,
        name="create-pending-transaction",
    ),

    # Update Transaction Status
    path(
        "<int:transaction_id>/status/",
        update_transaction_status,
        name="update-transaction-status",
    ),

    # User Dashboard Summary
    path(
        "dashboard/summary/",
        dashboard_summary,
        name="dashboard-summary",
    ),

    # Monthly Statement PDF
    path(
        "monthly-statement/",
        monthly_statement,
        name="monthly-statement",
    ),

    # Card Usage Analytics API (Monthly, Category, Utilization)
    path(
        "analytics/card-usage/",
        card_usage_analytics,
        name="card-usage-analytics",
    ),

    # Analytics Exports
    path(
        "analytics/export/csv/",
        export_analytics_csv,
        name="analytics-export-csv",
    ),
    path(
        "analytics/export/pdf/",
        export_analytics_pdf,
        name="analytics-export-pdf",
    ),

    # Filtered Transactions Export
    path(
        "export/csv/",
        export_transactions_csv_api,
        name="transactions-export-csv",
    ),

    # Fraud Logs & Review
    path(
        "fraud-logs/",
        list_fraud_logs,
        name="list-fraud-logs",
    ),
    path(
        "fraud-logs/<int:log_id>/review/",
        review_fraud_log,
        name="review-fraud-log",
    ),
]