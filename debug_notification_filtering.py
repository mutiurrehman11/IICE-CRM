#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from Admin.models import Student, StudentSession, Payments
from datetime import date

print("=== NOTIFICATION PAGE FILTERING ANALYSIS ===\n")

# Get all unpaid payments for active students (same as notify_late_fee_students)
unpaid_payments = Payments.objects.filter(
    amount=0,  # Unpaid payments
    studentsession__student__status='Active'
).select_related('studentsession__student', 'studentsession__session')

print(f"Total unpaid payment records: {unpaid_payments.count()}")

# Group payments by student (same logic as notify_late_fee_students)
student_payments = {}
for payment in unpaid_payments:
    if payment.studentsession and payment.studentsession.student:
        student = payment.studentsession.student
        if student not in student_payments:
            student_payments[student] = []
        student_payments[student].append(payment)

print(f"Students with unpaid payments: {len(student_payments)}")
print("\n=== FILTERING ANALYSIS ===\n")

students_processed = 0
students_skipped_no_email = 0
students_skipped_no_pending = 0
students_with_pending_fees = 0

for student, payments in student_payments.items():
    students_processed += 1
    print(f"Student: {student.student_name} ({student.rollno})")
    print(f"  Email: {student.email or 'None'}")
    
    # Check email filter
    if not student.email:
        students_skipped_no_email += 1
        print(f"  >>> SKIPPED: No email address")
        print()
        continue
    
    # Calculate pending amount
    pending_amount = 0
    session_details = []
    
    for payment in payments:
        if payment.studentsession and payment.studentsession.session:
            session_fee = payment.studentsession.session.fee
            pending_amount += session_fee
            session_details.append(f"    - {payment.studentsession.session.session_name}: Rs. {session_fee}")
    
    print(f"  Pending Amount: Rs. {pending_amount}")
    print(f"  Session Details:")
    for detail in session_details:
        print(detail)
    
    # Check pending amount filter
    if pending_amount <= 0:
        students_skipped_no_pending += 1
        print(f"  >>> SKIPPED: No pending amount (pending_amount <= 0)")
    else:
        students_with_pending_fees += 1
        print(f"  >>> INCLUDED: Will receive notification")
    
    print()

print("=== SUMMARY ===\n")
print(f"Total students processed: {students_processed}")
print(f"Students skipped (no email): {students_skipped_no_email}")
print(f"Students skipped (no pending amount): {students_skipped_no_pending}")
print(f"Students that will receive notifications: {students_with_pending_fees}")
print(f"\nThis explains why the Notification page shows {students_with_pending_fees} students instead of {students_processed}.")