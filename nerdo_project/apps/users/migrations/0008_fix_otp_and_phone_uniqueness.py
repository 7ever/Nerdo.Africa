from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_cleanup_old_avatar_paths'),
    ]

    operations = [
        # Fix otp_created_at: was auto_now=True (broken for expiry), now nullable and set manually
        migrations.AlterField(
            model_name='profile',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add unique constraint to phone_number (also null=True to handle blank profiles)
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
