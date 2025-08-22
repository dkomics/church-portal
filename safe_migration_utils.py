"""
Safe migration utilities to handle existing database objects
"""
from django.db import migrations, connection


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            );
        """, [table_name, column_name])
        return cursor.fetchone()[0]


class SafeCreateModel(migrations.CreateModel):
    """Custom CreateModel operation that checks if table exists first"""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        table_name = f"{app_label}_{self.name.lower()}"
        if not check_table_exists(table_name):
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        else:
            print(f"Table {table_name} already exists, skipping creation")


class SafeAddField(migrations.AddField):
    """Custom AddField operation that checks if column exists first"""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        # Handle ManyToManyField differently
        if self.field.many_to_many:
            # For ManyToMany fields, check the through table
            # The actual table name is: auth_user_profile_branches (for authentication.UserProfile.branches)
            through_table = f"{table_name}_{self.name}"
            
            if not check_table_exists(through_table):
                super().database_forwards(app_label, schema_editor, from_state, to_state)
            else:
                print(f"ManyToMany table {through_table} already exists, skipping creation")
            return
        
        # Get column name - handle different field types
        if hasattr(self.field, 'db_column') and self.field.db_column:
            column_name = self.field.db_column
        elif hasattr(self.field, 'column'):
            column_name = self.field.column
        else:
            # For ForeignKey and other fields, construct column name
            column_name = f"{self.name}_id" if self.field.many_to_one else self.name
        
        if not check_column_exists(table_name, column_name):
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        else:
            print(f"Column {column_name} already exists in {table_name}, skipping addition")


class SafeAlterField(migrations.AlterField):
    """Custom AlterField operation that handles existing fields safely"""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        # Get column name
        if hasattr(self.field, 'db_column') and self.field.db_column:
            column_name = self.field.db_column
        else:
            column_name = f"{self.name}_id" if self.field.many_to_one else self.name
        
        if check_column_exists(table_name, column_name):
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        else:
            print(f"Column {column_name} doesn't exist in {table_name}, skipping alteration")
