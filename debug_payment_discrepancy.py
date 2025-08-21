#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from Admin.models import Student, StudentSession, Payments
from datetime import date

print("=== PAYMENT PAGE vs NOTIFICATION PAGE DISCREPANCY ===\n")

# 1. Payment Page Logic: Students with payment_status = 'Unpaid'
print("1. PAYMENT PAGE LOGIC (Student.payment_status = 'Unpaid'):")
active_students = Student.objects.filter(status='Active')
unpaid_students_payment_page = [s for s in active_students if s.payment_status == 'Unpaid']
print(f"Students shown on Payment page: {len(unpaid_students_payment_page)}")
for student in unpaid_students_payment_page:
    print(f"  - {student.student_name} ({student.rollno}) - Status: {student.payment_status}")
    print(f"    Total Fee: Rs. {student.total_fee}, Paid: Rs. {student.total_paid}, Balance: Rs. {student.remaining_balance}")

print("\n" + "="*60 + "\n")

# 2. Notification Page Logic: Students with unpaid payment records (amount=0)
print("2. NOTIFICATION PAGE LOGIC (Unpaid payment records):")
unpaid_payments = Payments.objects.filter(
    amount=0,  # Unpaid payments
    studentsession__student__status='Active'
).select_related('studentsession__student', 'studentsession__session')

# Group by student
students_with_unpaid_records = {}
for payment in unpaid_payments:
    student = payment.studentsession.student
    if student.id not in students_with_unpaid_records:
        students_with_unpaid_records[student.id] = {
            'student': student,
            'unpaid_records': []
        }
    students_with_unpaid_records[student.id]['unpaid_records'].append(payment)

print(f"Students shown on Notification page: {len(students_with_unpaid_records)}")
for student_id, data in students_with_unpaid_records.items():
    student = data['student']
    unpaid_count = len(data['unpaid_records'])
    print(f"  - {student.student_name} ({student.rollno}) - {unpaid_count} unpaid record(s)")
    print(f"    Payment Status: {student.payment_status}")
    print(f"    Total Fee: Rs. {student.total_fee}, Paid: Rs. {student.total_paid}, Balance: Rs. {student.remaining_balance}")
    for payment in data['unpaid_records']:
        print(f"      * Unpaid: {payment.studentsession.session.session_name} - Due: {payment.studentsession.due_date}")

print("\n" + "="*60 + "\n")

# 3. Analysis
print("3. ANALYSIS:")
print("The discrepancy occurs because:")
print("- Payment page uses Student.payment_status which is calculated from total_fee vs total_paid")
print("- Notification page uses unpaid payment records (amount=0) regardless of overall payment status")
print("- A student can have unpaid payment records but still show as 'Paid' or 'Partial' if they've paid enough to cover their total fee")
print("\nSolution: Both pages should use the same logic for consistency.")