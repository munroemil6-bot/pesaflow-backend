import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Create or update the deployment administrator from environment variables."

    def handle(self, *args, **options):
        required = {
            "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL"),
            "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD"),
            "ADMIN_PHONE": os.getenv("ADMIN_PHONE"),
            "ADMIN_FULL_NAME": os.getenv("ADMIN_FULL_NAME"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            self.stdout.write("Admin bootstrap skipped; missing: " + ", ".join(missing))
            return

        try:
            admin, created = User.objects.get_or_create(
                email=required["ADMIN_EMAIL"].strip().lower(),
                defaults={
                    "phone": required["ADMIN_PHONE"].strip(),
                    "full_name": required["ADMIN_FULL_NAME"].strip(),
                },
            )
            admin.phone = required["ADMIN_PHONE"].strip()
            admin.full_name = required["ADMIN_FULL_NAME"].strip()
            admin.role = User.Role.ADMIN
            admin.is_active = True
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(required["ADMIN_PASSWORD"])
            admin.save()
        except Exception as exc:
            raise CommandError(f"Unable to bootstrap admin account: {exc}") from exc

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} deployment administrator."))
