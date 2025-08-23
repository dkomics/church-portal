"""
Management command to set up multiple branches in production
and distribute existing members across branches for proper testing
"""
from django.core.management.base import BaseCommand
from membership.models import Branch, Member


class Command(BaseCommand):
    help = 'Set up multiple branches and distribute members for production testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up production branches...')
        
        # Create JBFM Mwanza branch if it doesn't exist
        mwanza_branch, created = Branch.objects.get_or_create(
            code='MWZ',
            defaults={
                'name': 'JBFM Mwanza',
                'address': 'Mwanza, Tanzania',
                'phone': '+255 28 2500000',
                'email': 'mwanza@jbfm.org',
                'pastor_name': 'Pastor Mwanza',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {mwanza_branch.name}')
        else:
            self.stdout.write(f'✓ Exists: {mwanza_branch.name}')
        
        # Create JBFM Dar es Salaam branch if it doesn't exist
        dar_branch, created = Branch.objects.get_or_create(
            code='DAR',
            defaults={
                'name': 'JBFM Dar es Salaam',
                'address': 'Dar es Salaam, Tanzania',
                'phone': '+255 22 2000000',
                'email': 'dar@jbfm.org',
                'pastor_name': 'Pastor Dar',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Created: {dar_branch.name}')
        else:
            self.stdout.write(f'✓ Exists: {dar_branch.name}')
        
        # Get Arusha branch
        try:
            arusha_branch = Branch.objects.get(code='ARU')
        except Branch.DoesNotExist:
            self.stdout.write(self.style.ERROR('Arusha branch not found'))
            return
        
        # Check current member distribution
        total_members = Member.objects.count()
        arusha_members = Member.objects.filter(branch=arusha_branch).count()
        mwanza_members = Member.objects.filter(branch=mwanza_branch).count()
        dar_members = Member.objects.filter(branch=dar_branch).count()
        
        self.stdout.write(f'\nCurrent distribution:')
        self.stdout.write(f'  - {arusha_branch.name}: {arusha_members} members')
        self.stdout.write(f'  - {mwanza_branch.name}: {mwanza_members} members')
        self.stdout.write(f'  - {dar_branch.name}: {dar_members} members')
        self.stdout.write(f'  - Total: {total_members} members')
        
        # Only redistribute if all members are in Arusha
        if arusha_members == total_members and total_members > 6:
            self.stdout.write(f'\nRedistributing members across branches...')
            
            all_members = list(Member.objects.filter(branch=arusha_branch))
            
            # Calculate distribution (try to distribute evenly)
            members_per_branch = total_members // 3
            remainder = total_members % 3
            
            # Assign members to Mwanza
            mwanza_count = members_per_branch + (1 if remainder > 0 else 0)
            mwanza_members_list = all_members[:mwanza_count]
            for member in mwanza_members_list:
                member.branch = mwanza_branch
                member.save()
                self.stdout.write(f'  → Moved {member.full_name} to Mwanza')
            
            # Assign members to Dar
            dar_count = members_per_branch + (1 if remainder > 1 else 0)
            dar_members_list = all_members[mwanza_count:mwanza_count + dar_count]
            for member in dar_members_list:
                member.branch = dar_branch
                member.save()
                self.stdout.write(f'  → Moved {member.full_name} to Dar es Salaam')
            
            # Remaining members stay in Arusha
            remaining_in_arusha = total_members - mwanza_count - dar_count
            self.stdout.write(f'  → {remaining_in_arusha} members remain in Arusha')
            
        else:
            self.stdout.write(f'\nMembers already distributed or insufficient members for redistribution')
        
        # Show final distribution
        self.stdout.write(f'\nFinal distribution:')
        for branch in Branch.objects.filter(is_active=True):
            count = Member.objects.filter(branch=branch).count()
            self.stdout.write(f'  - {branch.name}: {count} members')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Branch setup completed successfully!'))
