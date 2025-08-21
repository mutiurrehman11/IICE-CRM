#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from Admin.models import Student, StudentSession, Payments
from datetime import date

print("=== DEBUGGING OVERDUE FEE ISSUE ===")
print(f"Today's date: {date.today()}")
print()

# Check all active students
active_students = Student.objects.filter(status='Active')
print(f"Total active students: {active_students.count()}")

overdue_count = 0
for student in active_students:
    print(f"\nStudent: {student.student_name} ({student.rollno})")
    print(f"Email: {student.email}")
    print(f"Total Fee: Rs. {student.total_fee}")
    print(f"Total Paid: Rs. {student.total_paid}")
    print(f"Remaining Balance: Rs. {student.remaining_balance}")
    print(f"Payment Status: {student.payment_status}")
    
    # Check sessions
    sessions = student.student_sessions.filter(status='Active')
    print(f"Active Sessions: {sessions.count()}")
    
    student_is_overdue = False
    for session in sessions:
        print(f"  - Session: {session.session.session_name}")
        print(f"    Due Date: {session.due_date}")
        print(f"    Session Balance: Rs. {session.session_balance}")
        
        if session.due_date and session.due_date < date.today() and session.session_balance > 0:
            print(f"    *** OVERDUE: {(date.today() - session.due_date).days} days ***")
            student_is_overdue = True
    
    if student_is_overdue:
        overdue_count += 1
        print(f"  >>> STUDENT IS OVERDUE <<<")
    
    print("-" * 50)

print(f"\n=== SUMMARY ===")
print(f"Total students with overdue fees: {overdue_count}")

# Also check the notification logic
print("\n=== CHECKING NOTIFICATION LOGIC ===")
from Admin.views import notify_late_fee_students
from django.test import RequestFactory

# Create a mock POST request
factory = RequestFactory()
request = factory.post('/notify-late-fee/')

# This would normally be called, but let's just check the logic
print("Notification logic would process the same students found above.")