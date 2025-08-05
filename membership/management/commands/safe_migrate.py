from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.db.utils import ProgrammingError
import sys


class Command(BaseCommand):
    help = 'Safely run migrations, handling conflicts gracefully'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fake-initial',
            action='store_true',
            help='Mark initial migrations as already applied',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting safe migration process...'))
        
        try:
            # First, check if we can run migrations normally
            self.stdout.write('Checking migration status...')
            call_command('migrate', '--check', verbosity=0)
            self.stdout.write(self.style.SUCCESS('No migrations needed.'))
            return
            
        except SystemExit:
            # Migrations are needed, proceed with safe migration
            self.stdout.write('Migrations needed, proceeding with safe migration...')
            
        try:
            # Try normal migration first
            self.stdout.write('Attempting normal migration...')
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Normal migration completed successfully.'))
            
        except ProgrammingError as e:
            error_msg = str(e).lower()
            
            if 'already exists' in error_msg:
                self.stdout.write(
                    self.style.WARNING(f'Migration conflict detected: {e}')
                )
                self.stdout.write('Attempting to resolve with --fake-initial...')
                
                try:
                    # Mark initial migrations as fake
                    call_command('migrate', '--fake-initial', verbosity=1)
                    self.stdout.write(self.style.SUCCESS('Fake initial migration completed.'))
                    
                    # Now run remaining migrations
                    self.stdout.write('Running remaining migrations...')
                    call_command('migrate', verbosity=1)
                    self.stdout.write(self.style.SUCCESS('All migrations completed successfully.'))
                    
                except Exception as fake_error:
                    self.stdout.write(
                        self.style.ERROR(f'Fake migration also failed: {fake_error}')
                    )
                    
                    # Last resort: try to handle specific table conflicts
                    self.handle_specific_conflicts()
                    
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unexpected migration error: {e}')
                )
                sys.exit(1)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Migration failed with unexpected error: {e}')
            )
            sys.exit(1)

    def handle_specific_conflicts(self):
        """Handle specific known migration conflicts"""
        self.stdout.write('Attempting to resolve specific migration conflicts...')
        
        try:
            with connection.cursor() as cursor:
                # Check if problematic columns exist
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'membership_member' 
                    AND column_name IN ('age_category', 'membership_id');
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                if existing_columns:
                    self.stdout.write(
                        f'Found existing columns: {existing_columns}'
                    )
                    
                    # Mark specific migrations as fake
                    self.stdout.write('Marking conflicting migrations as fake...')
                    call_command('migrate', 'membership', '0002', '--fake', verbosity=1)
                    
                    # Run remaining migrations
                    call_command('migrate', verbosity=1)
                    self.stdout.write(self.style.SUCCESS('Conflict resolution completed.'))
                else:
                    self.stdout.write('No specific conflicts found, running normal migration...')
                    call_command('migrate', verbosity=1)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Conflict resolution failed: {e}')
            )
            self.stdout.write('Attempting final fallback migration...')
            
            try:
                # Final fallback: fake all migrations and start fresh
                call_command('migrate', '--fake', verbosity=1)
                self.stdout.write(self.style.WARNING('All migrations marked as fake. Manual verification may be needed.'))
            except Exception as final_error:
                self.stdout.write(
                    self.style.ERROR(f'All migration attempts failed: {final_error}')
                )
                sys.exit(1)
