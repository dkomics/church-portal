from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile
from membership.models import Branch


class Command(BaseCommand):
    help = 'Assign users to branches and update their roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to assign to a branch',
        )
        parser.add_argument(
            '--branch-code',
            type=str,
            help='Branch code to assign user to',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['member', 'secretary', 'pastor', 'branch_admin', 'admin'],
            help='Role to assign to the user',
        )
        parser.add_argument(
            '--make-primary',
            action='store_true',
            help='Make this branch the user\'s primary branch',
        )

    def handle(self, *args, **options):
        if options['username'] and options['branch_code']:
            try:
                user = User.objects.get(username=options['username'])
                branch = Branch.objects.get(code=options['branch_code'])
                
                # Get or create user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Add branch to user's accessible branches
                profile.branches.add(branch)
                
                # Set as primary branch if requested
                if options['make_primary']:
                    profile.primary_branch = branch
                
                # Update role if provided
                if options['role']:
                    profile.role = options['role']
                
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully assigned {user.username} to {branch.name}'
                    )
                )
                
                if options['role']:
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated role to: {options["role"]}')
                    )
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{options["username"]}" not found')
                )
            except Branch.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Branch with code "{options["branch_code"]}" not found')
                )
        else:
            # List all users and their branch assignments
            self.stdout.write(self.style.SUCCESS('Current user-branch assignments:'))
            self.stdout.write('-' * 80)
            
            for profile in UserProfile.objects.select_related('user', 'primary_branch').prefetch_related('branches'):
                user = profile.user
                branches = list(profile.branches.all())
                primary = profile.primary_branch
                
                self.stdout.write(f'User: {user.username} ({user.get_full_name() or "No full name"})')
                self.stdout.write(f'  Role: {profile.get_role_display()}')
                self.stdout.write(f'  Primary Branch: {primary.name if primary else "None"}')
                self.stdout.write(f'  Accessible Branches: {", ".join([b.name for b in branches]) if branches else "None"}')
                self.stdout.write('')
            
            self.stdout.write(self.style.SUCCESS('\nUsage examples:'))
            self.stdout.write('  python manage.py assign_user_branches --username admin --branch-code ARU --role admin --make-primary')
            self.stdout.write('  python manage.py assign_user_branches --username pastor1 --branch-code DAR --role pastor')
