# Generated by Django 5.1.8 on 2025-04-23 23:46

import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vital_records", "0004_vitalrecordsrequest_county_of_birth_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="vitalrecordsrequest",
            name="date_of_birth",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="vitalrecordsrequest",
            name="status",
            field=django_fsm.FSMField(
                choices=[
                    ("started", "Started"),
                    ("eligibility_completed", "Eligibility Completed"),
                    ("statement_completed", "Sworn Statement Completed"),
                    ("name_completed", "Name Completed"),
                    ("county_completed", "County Completed"),
                    ("dob_completed", "Date of Birth Completed"),
                    ("submitted", "Request Submitted"),
                ],
                default="started",
                max_length=50,
            ),
        ),
    ]
