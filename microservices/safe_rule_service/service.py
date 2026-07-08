"""
Safe Rule Service
-----------------
Scans all Submission records where status='processed' and sets
safety_rule='safe' if it is not already set to 'safe'.
"""

import os
import sys
import django

# ---------------------------------------------------------------------------
# Bootstrap Django so we can use its ORM outside of the main app process
# ---------------------------------------------------------------------------
# Point to the Django project's settings module.
# The DB_PATH env-var lets the container mount the same SQLite file.
DB_PATH = os.environ.get("DB_PATH", "/app/db.sqlite3")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Override only the database path; everything else comes from settings.py
import django.conf as django_conf  # noqa: E402

# We configure Django settings programmatically so this script can run
# standalone inside a minimal container (no need to copy full config/).
django_conf.settings.configure(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DB_PATH,
        }
    },
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "photos",
    ],
    AUTH_USER_MODEL="photos.User",
    USE_TZ=True,
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)

django.setup()

# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------
from photos.models import Submission  # noqa: E402  (must come after setup)


def run():
    queryset = Submission.objects.filter(
        status=Submission.StatusChoices.PROCESSED
    ).exclude(
        safety_rule=Submission.SafetyRuleChoices.SAFE
    )

    count = queryset.count()
    if count == 0:
        print("[safe-rule-service] No processed submissions need updating.")
        return

    updated = queryset.update(safety_rule=Submission.SafetyRuleChoices.SAFE)
    print(f"[safe-rule-service] Updated {updated} submission(s) → safety_rule='safe'.")


if __name__ == "__main__":
    run()
