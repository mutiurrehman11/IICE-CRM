#!/usr/bin/env python
import os

print("=== FIXING EXSTUDENTS TEMPLATE ===")

def create_clean_exstudents_template():
    """Create a clean ExStudents template based on Students template"""
    
    print("Creating clean ExStudents template...")
    
    # Read the Students template as a reference
    try:
        with open('templates/Admin/Students.html', 'r', encoding='utf-8') as f:
            students_content = f.read()
    except Exception as e:
        print(f"Error reading Students template: {e}")
        return False
    
    # Create a clean ExStudents template by modifying the Students template
    exstudents_content = students_content.replace(
        'Students', 'Ex-Students'
    ).replace(
        'Active Students', 'Inactive Students'
    ).replace(
        "{% url 'Students' %}", "{% url 'ExStudents' %}"
    ).replace(
        'class="menu-item active"', 'class="menu-item"'
    )
    
    # Update the specific menu item for ExStudents to be active
    exstudents_content = exstudents_content.replace(
        '<a href="{% url \'ExStudents\' %}" class="menu-link">',
        '<a href="{% url \'ExStudents\' %}" class="menu-link active">'
    )
    
    # Write the clean template
    try:
        with open('templates/Admin/ExStudents_clean.html', 'w', encoding='utf-8') as f:
            f.write(exstudents_content)
        print("✅ Clean ExStudents template created as ExStudents_clean.html")
        return True
    except Exception as e:
        print(f"❌ Error creating clean template: {e}")
        return False

def backup_and_replace():
    """Backup current template and replace with clean version"""
    
    print("Backing up and replacing template...")
    
    try:
        # Backup current corrupted template
        if os.path.exists('templates/Admin/ExStudents.html'):
            os.rename('templates/Admin/ExStudents.html', 'templates/Admin/ExStudents_corrupted.html')
            print("✅ Backed up corrupted template as ExStudents_corrupted.html")
        
        # Replace with clean version
        if os.path.exists('templates/Admin/ExStudents_clean.html'):
            os.rename('templates/Admin/ExStudents_clean.html', 'templates/Admin/ExStudents.html')
            print("✅ Replaced with clean template")
            return True
        else:
            print("❌ Clean template not found")
            return False
            
    except Exception as e:
        print(f"❌ Error during backup and replace: {e}")
        return False

# Run the fix
try:
    if create_clean_exstudents_template():
        if backup_and_replace():
            print("\n🎉 EXSTUDENTS TEMPLATE FIXED SUCCESSFULLY!")
            print("The template should now display correctly without duplications.")
        else:
            print("\n❌ Failed to replace template")
    else:
        print("\n❌ Failed to create clean template")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()