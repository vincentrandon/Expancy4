# Generated by Django 4.0.5 on 2022-06-20 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0003_alter_companyfileresult_company_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transporterfileresults',
            name='transporter_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='files.transporterfile'),
        ),
    ]
