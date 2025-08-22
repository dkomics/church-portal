#!/usr/bin/env python
"""
Safe migration script for multi-branch church portal deployment
This script ensures existing data is preserved during the upgrade
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import transaction
import subprocess
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal.settings')
django.setup()

from membership.models import Member, Branch
from authentication.models import UserProfile


def create_backup():
    """Create database backup before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_before_migration_{timestamp}.json"
    
    print(f"Creating backup: {backup_file}")
    try:
        execute_from_command_line(['manage.py', 'dumpdata', '--output', backup_file])
        print(f"✅ Backup created successfully: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None


def test_migrations():
    """Test migrations without applying them"""
    print("Testing migrations (dry run)...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--dry-run'])
        print("✅ Migration dry run successful")
        return True
    except Exception as e:
        print(f"❌ Migration dry run failed: {e}")
        return False


def apply_migrations():
    """Apply migrations safely"""
    print("Applying migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def setup_default_branch():
    """Create default branch and assign existing members"""
    print("Setting up default branch...")
    
    try:
        with transaction.atomic():
            # Create default branch if it doesn't exist
            default_branch, created = Branch.objects.get_or_create(
                code='MAIN',
                defaults={
                    'name': 'JBFM Main Branch',
                    'address': 'Main Church Location',
                    'pastor_name': 'Pastor Main',
                    'is_active': True
                }
            )
            
            if created:
                print(f"✅ Created default branch: {default_branch.name}")
            else:
                print(f"✅ Using existing branch: {default_branch.name}")
            
            # Assign members without branches to default branch
            members_without_branch = Member.objects.filter(branch__isnull=True)
            count = members_without_branch.count()
            
            if count > 0:
                members_without_branch.update(branch=default_branch)
                print(f"✅ Assigned {count} existing members to {default_branch.name}")
            else:
                print("✅ All members already have branch assignments")
            
            return True
            
    except Exception as e:
        print(f"❌ Default branch setup failed: {e}")
        return False


def verify_data_integrity():
    """Verify that existing data is intact after migration"""
    print("Verifying data integrity...")
    
    try:
        # Check that all members have branches
        members_without_branch = Member.objects.filter(branch__isnull=True).count()
        if members_without_branch > 0:
            print(f"⚠️  Warning: {members_without_branch} members without branch assignment")
            return False
        
        # Check that existing member data is intact
        total_members = Member.objects.count()
        print(f"✅ Total members: {total_members}")
        
        # Check branches exist
        total_branches = Branch.objects.count()
        print(f"✅ Total branches: {total_branches}")
        
        # Verify user profiles
        total_profiles = UserProfile.objects.count()
        print(f"✅ Total user profiles: {total_profiles}")
        
        print("✅ Data integrity verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Data integrity check failed: {e}")
        return False


def rollback_from_backup(backup_file):
    """Rollback database from backup file"""
    if not backup_file or not os.path.exists(backup_file):
        print("❌ No backup file available for rollback")
        return False
    
    print(f"Rolling back from backup: {backup_file}")
    try:
        # Flush current database
        execute_from_command_line(['manage.py', 'flush', '--noinput'])
        # Load backup data
        execute_from_command_line(['manage.py', 'loaddata', backup_file])
        print("✅ Rollback completed successfully")
        return True
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False


def main():
    """Main migration process"""
    print("🚀 Starting safe migration process...")
    print("=" * 50)
    
    # Step 1: Create backup
    backup_file = create_backup()
    if not backup_file:
        print("❌ Cannot proceed without backup. Aborting.")
        return False
    
    # Step 2: Test migrations
    if not test_migrations():
        print("❌ Migration test failed. Aborting.")
        return False
    
    # Step 3: Apply migrations
    if not apply_migrations():
        print("❌ Migration failed. Consider rollback.")
        rollback_choice = input("Do you want to rollback? (y/N): ")
        if rollback_choice.lower() == 'y':
            rollback_from_backup(backup_file)
        return False
    
    # Step 4: Setup default branch and assign members
    if not setup_default_branch():
        print("❌ Default branch setup failed. Consider rollback.")
        rollback_choice = input("Do you want to rollback? (y/N): ")
        if rollback_choice.lower() == 'y':
            rollback_from_backup(backup_file)
        return False
    
    # Step 5: Verify data integrity
    if not verify_data_integrity():
        print("❌ Data integrity check failed. Consider rollback.")
        rollback_choice = input("Do you want to rollback? (y/N): ")
        if rollback_choice.lower() == 'y':
            rollback_from_backup(backup_file)
        return False
    
    print("=" * 50)
    print("✅ Migration completed successfully!")
    print(f"📁 Backup saved as: {backup_file}")
    print("🎉 Your church portal now supports multi-branch functionality!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
