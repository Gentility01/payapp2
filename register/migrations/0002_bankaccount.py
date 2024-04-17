# Generated by Django 4.2.3 on 2024-04-15 05:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("register", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "bank_name",
                    models.CharField(
                        choices=[
                            ("BANK_OF_AMERICA", "Bank of America"),
                            ("CHINA_UNION_PAY", "China Union Pay"),
                            ("CREDIT_AGRICOLE", "Credit Agricole"),
                            ("CREDIT_SUISSE", "Credit Suisse"),
                            ("DEUTSCHE_BANK", "Deutsche Bank"),
                            ("JPMORGAN_CHASE", "JPMorgan Chase"),
                            ("MASTERCARD", "Mastercard"),
                            ("ACCESS_BANK", "Access Bank"),
                            ("FIRST_BANK", "First Bank of Nigeria"),
                            ("GTBANK", "Guaranty Trust Bank"),
                            ("ZENITH_BANK", "Zenith Bank"),
                            ("UBA", "United Bank for Africa"),
                            ("STANBIC_IBTC", "Stanbic IBTC Bank"),
                        ],
                        default="ACCESS_BANK",
                        max_length=50,
                    ),
                ),
                ("account_number", models.CharField(max_length=50)),
                ("routing_number", models.CharField(max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Bank Accounts",
            },
        ),
    ]