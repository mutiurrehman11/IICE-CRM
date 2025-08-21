#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from Admin.models import Student, StudentSession, Payments
from datetime import date

print("=== FINAL DISCREPANCY ANALYSIS ===\n")
print("USER REPORTED: Payment page shows 1 student, Notification page shows 3 students\n")

# 1. Payment Page Logic
print("1. PAYMENT PAGE ANALYSIS:")
print("   Logic: Shows students where Student.payment_status == 'Unpaid'")
active_students = Student.objects.filter(status='Active')
unpaid_students_payment_page = [s for s in active_students if s.payment_status == 'Unpaid']
print(f"   Result: {len(unpaid_students_payment_page)} student(s)")
for student in unpaid_students_payment_page:
    print(f"   - {student.student_name} ({student.rollno}) - Status: {student.payment_status}")
    print(f"     Total Fee: Rs. {student.total_fee}, Paid: Rs. {student.total_paid}, Balance: Rs. {student.remaining_balance}")

print("\n" + "="*70 + "\n")

# 2. Notification Page Logic
print("2. NOTIFICATION PAGE ANALYSIS:")
print("   Logic: Shows students with unpaid payment records (amount=0) who have email and pending_amount > 0")

# Get unpaid payments
unpaid_payments = Payments.objects.filter(
    amount=0,
    studentsession__student__status='Active'
).select_related('studentsession__student', 'studentsession__session')

# Group by student
student_payments = {}
for payment in unpaid_payments:
    if payment.studentsession and payment.studentsession.student:
        student = payment.studentsession.student
        if student not in student_payments:
            student_payments[student] = []
        student_payments[student].append(payment)

# Apply notification filters
notification_students = []
for student, payments in student_payments.items():
    # Filter 1: Must have email
    if not student.email:
        continue
    
    # Filter 2: Must have pending amount > 0
    pending_amount = sum(p.studentsession.session.fee for p in payments if p.studentsession and p.studentsession.session)
    if pending_amount <= 0:
        continue
    
    notification_students.append((student, pending_amount))

print(f"   Result: {len(notification_students)} student(s)")
for student, pending_amount in notification_students:
    print(f"   - {student.student_name} ({student.rollno}) - Pending: Rs. {pending_amount}")
    print(f"     Payment Status: {student.payment_status}")
    print(f"     Total Fee: Rs. {student.total_fee}, Paid: Rs. {student.total_paid}, Balance: Rs. {student.remaining_balance}")

print("\n" + "="*70 + "\n")

# 3. Root Cause Analysis
print("3. ROOT CAUSE ANALYSIS:")
print("\nThe discrepancy occurs because the two pages use completely different logic:")
print("\nPAYMENT PAGE:")
print("- Uses Student.payment_status property")
print("- Calculated as: remaining_balance = total_fee - total_paid")
print("- Status = 'Unpaid' if total_paid == 0, 'Partial' if 0 < total_paid < total_fee, 'Paid' if total_paid >= total_fee")
print("- Considers ALL sessions (active + inactive) in total_fee calculation")
print("\nNOTIFICATION PAGE:")
print("- Uses unpaid payment records (Payments.amount = 0)")
print("- Groups by student and calculates pending amount from session fees")
print("- Only considers students with email addresses")
print("- A student can have 'Paid' status but still have unpaid payment records")

print("\n" + "="*70 + "\n")

# 4. Examples of the discrepancy
print("4. EXAMPLES OF THE DISCREPANCY:")
for student, pending_amount in notification_students:
    if student.payment_status != 'Unpaid':
        print(f"\nEXAMPLE: {student.student_name} ({student.rollno})")
        print(f"- Shows on Notification page: YES (has unpaid records, pending Rs. {pending_amount})")
        print(f"- Shows on Payment page: NO (payment_status = '{student.payment_status}')")
        print(f"- Reason: Student has paid enough to cover total fees but has specific unpaid payment records")

print("\n" + "="*70 + "\n")

# 5. Solution
print("5. RECOMMENDED SOLUTION:")
print("\nTo fix this discrepancy, both pages should use the same logic. Options:")
print("\nOption A: Use Payment Status Logic (Recommended)")
print("- Both pages show students where payment_status == 'Unpaid'")
print("- More intuitive: students who haven't paid their total fees")
print("- Simpler and more consistent")
print("\nOption B: Use Unpaid Records Logic")
print("- Both pages show students with unpaid payment records")
print("- More granular: tracks specific payment installments")
print("- May show students who have technically paid their total fees")
print("\nOption C: Hybrid Approach")
print("- Show students who are either 'Unpaid' OR have overdue unpaid records")
print("- Most comprehensive but potentially confusing")

print(f"\n=== CURRENT COUNTS ===\n")
print(f"Payment page shows: {len(unpaid_students_payment_page)} student(s)")
print(f"Notification page shows: {len(notification_students)} student(s)")
print(f"User reported seeing: 1 vs 3 students")
print(f"\nNote: The user's count of 3 might be from a different time or filtered view.")