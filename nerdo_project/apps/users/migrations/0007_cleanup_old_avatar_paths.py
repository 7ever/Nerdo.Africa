# Generated manually on 2025-12-09

from django.db import migrations


def cleanup_old_avatar_paths(apps, schema_editor):
    """Update profiles with old default avatar path to null"""
    Profile = apps.get_model('users', 'Profile')
    
    # Update profiles with old default path
    old_default_count = Profile.objects.filter(avatar='defaults/default_avatar.png').count()
    if old_default_count > 0:
        Profile.objects.filter(avatar='defaults/default_avatar.png').update(avatar=None)
    
    # Also clean up empty strings
    empty_count = Profile.objects.filter(avatar='').count()
    if empty_count > 0:
        Profile.objects.filter(avatar='').update(avatar=None)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_profile_avatar'),
    ]

    operations = [
        migrations.RunPython(cleanup_old_avatar_paths, reverse_code=migrations.RunPython.noop),
    ]
