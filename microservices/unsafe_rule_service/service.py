"""
Unsafe Rule Service
-------------------
Scans all Submission records where status='failed' and sets
safety_rule='unsafe' if it is not already set to 'unsafe'.
"""

import os
import django
import django.conf as django_conf

# ---------------------------------------------------------------------------
# Bootstrap Django ORM
# ---------------------------------------------------------------------------
DB_PATH = os.environ.get("DB_PATH", "/app/db.sqlite3")

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
from photos.models import Submission  # noqa: E402


def run():
    queryset = Submission.objects.filter(
        status=Submission.StatusChoices.FAILED
    ).exclude(
        safety_rule=Submission.SafetyRuleChoices.UNSAFE
    )

    count = queryset.count()
    if count == 0:
        print("[unsafe-rule-service] No failed submissions need updating.")
        return

    updated = queryset.update(safety_rule=Submission.SafetyRuleChoices.UNSAFE)
    print(f"[unsafe-rule-service] Updated {updated} submission(s) → safety_rule='unsafe'.")


if __name__ == "__main__":
    run()
