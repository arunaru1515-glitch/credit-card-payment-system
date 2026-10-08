from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_card_credit_limit"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="is_blocked",
            field=models.BooleanField(default=False),
        ),
    ]