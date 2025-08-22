from django.core.management.base import BaseCommand
from django.utils import timezone
from membership.models import Branch, NewsCategory
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Set up initial branches and news categories for the church portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample branches and categories',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up church branches...'))
        
        # Create default branch if none exists
        if not Branch.objects.exists():
            default_branch = Branch.objects.create(
                name='JBFM Arusha - Main Branch',
                code='ARU',
                address='Arusha, Tanzania',
                pastor_name='Pastor Main',
                established_date=timezone.now().date(),
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created default branch: {default_branch.name}')
            )
        
        # Create sample branches if requested
        if options['create_sample_data']:
            sample_branches = [
                {
                    'name': 'JBFM Dar es Salaam',
                    'code': 'DAR',
                    'address': 'Dar es Salaam, Tanzania',
                    'pastor_name': 'Pastor Dar',
                },
                {
                    'name': 'JBFM Mwanza',
                    'code': 'MWZ',
                    'address': 'Mwanza, Tanzania',
                    'pastor_name': 'Pastor Mwanza',
                },
                {
                    'name': 'JBFM Dodoma',
                    'code': 'DOD',
                    'address': 'Dodoma, Tanzania',
                    'pastor_name': 'Pastor Dodoma',
                },
            ]
            
            for branch_data in sample_branches:
                branch, created = Branch.objects.get_or_create(
                    code=branch_data['code'],
                    defaults={
                        'name': branch_data['name'],
                        'address': branch_data['address'],
                        'pastor_name': branch_data['pastor_name'],
                        'established_date': timezone.now().date(),
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created branch: {branch.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Branch already exists: {branch.name}')
                    )
        
        # Create default news categories
        default_categories = [
            {'name': 'Church Announcements', 'color': '#007bff', 'description': 'General church announcements'},
            {'name': 'Events', 'color': '#28a745', 'description': 'Upcoming church events'},
            {'name': 'Prayer Requests', 'color': '#ffc107', 'description': 'Prayer requests and updates'},
            {'name': 'Ministry Updates', 'color': '#17a2b8', 'description': 'Updates from various ministries'},
            {'name': 'Urgent', 'color': '#dc3545', 'description': 'Urgent announcements'},
        ]
        
        for category_data in default_categories:
            category, created = NewsCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'color': category_data['color'],
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created news category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'News category already exists: {category.name}')
                )
        
        # Update existing members to have a branch if they don't have one
        from membership.models import Member
        members_without_branch = Member.objects.filter(branch__isnull=True)
        if members_without_branch.exists():
            default_branch = Branch.objects.first()
            if default_branch:
                updated_count = members_without_branch.update(branch=default_branch)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned {updated_count} existing members to {default_branch.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully completed branch setup!')
        )
