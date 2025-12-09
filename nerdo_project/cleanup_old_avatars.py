import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'p:\WEB DEV\Emobilis\WebDev Fin Project\Nerdo.Africa - Copy\nerdo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nerdo_project.settings')
django.setup()

# Now import and run cleanup
from apps.users.models import Profile

# Find and update profiles with old default path
old_default_count = Profile.objects.filter(avatar='defaults/default_avatar.png').count()
print(f'Found {old_default_count} profiles with old default path')

if old_default_count > 0:
    updated = Profile.objects.filter(avatar='defaults/default_avatar.png').update(avatar=None)
    print(f'✅ Updated {updated} profiles to use null avatar (will show default from static/images/avatar.png)')

# Also check for empty string avatars
empty_count = Profile.objects.filter(avatar='').count()
if empty_count > 0:
    updated_empty = Profile.objects.filter(avatar='').update(avatar=None)
    print(f'✅ Updated {updated_empty} profiles with empty avatar paths')

print('\n✅ Cleanup complete! All profiles without custom avatars will now use static/images/avatar.png')
