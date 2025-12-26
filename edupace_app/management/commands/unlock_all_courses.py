"""
Django Management Command: Unlock All Courses

This command safely unlocks all courses by setting is_locked = False
for all courses where it is currently True.

Usage:
    python manage.py unlock_all_courses
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from edupace_app.models import Course


class Command(BaseCommand):
    help = 'Unlock all courses by setting is_locked = False'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be executed without actually running',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            # Count locked courses before
            locked_count = Course.objects.filter(is_locked=True).count()
            
            if locked_count == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ No locked courses found. All courses are already unlocked.')
                )
                return
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'Would unlock {locked_count} course(s)')
                )
                return
            
            # Unlock all courses using a safe transaction
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE edupace_app_course SET is_locked = %s WHERE is_locked = %s",
                        [False, True]
                    )
                    updated_count = cursor.rowcount
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully unlocked {updated_count} course(s)'
                )
            )
            
            # Verify
            remaining_locked = Course.objects.filter(is_locked=True).count()
            if remaining_locked == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ Verification: All courses are now unlocked.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Warning: {remaining_locked} course(s) are still locked.'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error occurred: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('All changes have been rolled back automatically')
            )
            raise

