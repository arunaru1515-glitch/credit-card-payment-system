from django.contrib import admin
from .models import User, Card


admin.site.register(User)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "card_type",
        "masked_card_number",
        "last_four_digits",
        "created_at",
    )