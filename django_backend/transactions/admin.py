from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count

from .models import Transaction


@admin.action(description="Export selected transactions to CSV")
def export_transactions_csv(modeladmin, request, queryset):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="transactions.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Transaction ID",
        "User",
        "Card",
        "Amount",
        "Status",
        "Transaction Date",
    ])

    for transaction in queryset:
        writer.writerow([
            transaction.id,
            transaction.user.username,
            (
                transaction.card.last_four_digits
                if transaction.card
                else ""
            ),
            transaction.amount,
            transaction.status,
            transaction.transaction_date,
        ])

    return response


@admin.action(description="View Daily Payment Summary")
def daily_payment_summary(modeladmin, request, queryset):

    today = timezone.localdate()

    today_transactions = Transaction.objects.filter(
        transaction_date__date=today
    )

    total_transactions = today_transactions.count()

    successful_transactions = today_transactions.filter(
        status="SUCCESS"
    )

    failed_transactions = today_transactions.filter(
        status="FAILED"
    )

    pending_transactions = today_transactions.filter(
        status="PENDING"
    )

    successful_count = successful_transactions.count()
    failed_count = failed_transactions.count()
    pending_count = pending_transactions.count()

    total_amount = today_transactions.aggregate(
        total=Sum("amount")
    )["total"] or 0

    successful_amount = successful_transactions.aggregate(
        total=Sum("amount")
    )["total"] or 0

    response = HttpResponse(
        content_type="text/html"
    )

    response.write("""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Daily Payment Summary</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background: #f5f5f5;
                }

                .container {
                    max-width: 700px;
                    margin: auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }

                h1 {
                    margin-bottom: 10px;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 25px;
                }

                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }

                th {
                    background: #333;
                    color: white;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h1>Daily Payment Summary</h1>
    """)

    response.write(
        f"<p><strong>Date:</strong> {today}</p>"
    )

    response.write("""
                <table>
                    <tr>
                        <th>Payment Metric</th>
                        <th>Value</th>
                    </tr>
    """)

    response.write(
        f"<tr><td>Total Transactions</td>"
        f"<td>{total_transactions}</td></tr>"
    )

    response.write(
        f"<tr><td>Successful Transactions</td>"
        f"<td>{successful_count}</td></tr>"
    )

    response.write(
        f"<tr><td>Failed Transactions</td>"
        f"<td>{failed_count}</td></tr>"
    )

    response.write(
        f"<tr><td>Pending Transactions</td>"
        f"<td>{pending_count}</td></tr>"
    )

    response.write(
        f"<tr><td>Total Payment Amount</td>"
        f"<td>&#8377;{total_amount}</td></tr>"
    )

    response.write(
        f"<tr><td>Successful Payment Amount</td>"
        f"<td>&#8377;{successful_amount}</td></tr>"
    )

    response.write("""
                </table>
            </div>
        </body>
        </html>
    """)

    return response


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "card",
        "amount",
        "status",
        "transaction_date",
    )

    list_filter = (
        "status",
        "transaction_date",
        "amount",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "-transaction_date",
    )

    actions = [
        export_transactions_csv,
        daily_payment_summary,
    ]