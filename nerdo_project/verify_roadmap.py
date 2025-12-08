
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nerdo_project.settings')
django.setup()

from apps.learning.utils import generate_roadmap_topics

print("--- Roadmaps Verification ---")

query = "Learn Python"
print(f"\n[BEGINNER] Query: '{query}'")
topics_beginner = generate_roadmap_topics(query, skill_level="beginner", duration_weeks=4)
for t in topics_beginner:
    print(f"- {t}")

print(f"\n[ADVANCED] Query: '{query}'")
topics_advanced = generate_roadmap_topics(query, skill_level="advanced", duration_weeks=12)
for t in topics_advanced:
    print(f"- {t}")

print("\n[UNIQUENESS CHECK] Generating Beginner again:")
topics_beginner_2 = generate_roadmap_topics(query, skill_level="beginner", duration_weeks=4)
for t in topics_beginner_2:
    print(f"- {t}")

if topics_beginner != topics_beginner_2:
    print("\nSUCCESS: Roadmaps are different/unique!")
else:
    print("\nWARNING: Roadmaps are identical.")
