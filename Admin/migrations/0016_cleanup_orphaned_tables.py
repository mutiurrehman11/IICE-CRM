from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('Admin', '0015_merge_20250815_1952'),  # Your latest migration
    ]

    operations = [
        # First remove any remaining data and constraints
        migrations.RunSQL(
            "DELETE FROM admin_installment;",
            reverse_sql="-- No reverse needed"
        ),
        migrations.RunSQL(
            "DELETE FROM admin_studentfee;", 
            reverse_sql="-- No reverse needed"
        ),
        # Then drop the tables
        migrations.RunSQL(
            "DROP TABLE IF EXISTS admin_installment;",
            reverse_sql="-- No reverse needed"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS admin_studentfee;",
            reverse_sql="-- No reverse needed"
        ),
    ]