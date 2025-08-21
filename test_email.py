#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from Admin.models import Student

print("Testing email configuration...")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

print("\nChecking students with pending fees...")
students = Student.objects.all()
print(f"Total students: {students.count()}")

for student in students[:5]:  # Check first 5 students
    print(f"\nStudent: {student.student_name}")
    print(f"Email: {student.email}")
    print(f"Total Fee: Rs. {student.total_fee:,.0f}")
    print(f"Total Paid: Rs. {student.total_paid:,.0f}")
    print(f"Remaining Balance: Rs. {student.remaining_balance:,.0f}")
    print(f"Payment Status: {student.payment_status}")
    
    # Check sessions
    sessions = student.studentsession_set.all()
    print(f"Sessions: {sessions.count()}")
    for session in sessions:
        print(f"  - {session.session.session_name} ({session.status}): Balance Rs. {session.session_balance:,.0f}")

print("\nTesting email sending...")
try:
    send_mail(
        subject='Test Email from IICE CRM',
        message='This is a test email to verify email configuration.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
        fail_silently=False,
    )
    print("✓ Test email sent successfully!")
except Exception as e:
    print(f"✗ Email sending failed: {str(e)}")