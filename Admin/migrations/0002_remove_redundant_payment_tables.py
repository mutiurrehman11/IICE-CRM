
# Generated migration to remove redundant payment tables

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0001_initial'),  # Replace with your latest migration
    ]

    operations = [
        # Remove redundant tables
        migrations.DeleteModel(
            name='StudentFee',
        ),
        migrations.DeleteModel(
            name='Installment',
        ),
        
        # Remove redundant field
        migrations.RemoveField(
            model_name='studentsession',
            name='fee_paid',
        ),
    ]
