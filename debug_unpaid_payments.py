from Admin.models import Payments, StudentSession, Student
from datetime import date

print("=== DEBUGGING UNPAID PAYMENTS ===")
print(f"Today's date: {date.today()}")
print()

# Find all unpaid payments (amount = 0)
unpaid_payments = Payments.objects.filter(amount=0).select_related(
    'studentsession__student', 'studentsession__session'
)

print(f"Total unpaid payments found: {unpaid_payments.count()}")
print()

for payment in unpaid_payments:
    if payment.studentsession and payment.studentsession.student.status == 'Active':
        student = payment.studentsession.student
        session = payment.studentsession.session
        due_date = payment.date
        days_diff = (due_date - date.today()).days
        days_overdue = abs(days_diff) if days_diff < 0 else 0
        
        print(f"Student: {student.student_name}")
        print(f"Session: {session.session_name if session else 'N/A'}")
        print(f"Due Date: {due_date}")
        print(f"Days Difference: {days_diff}")
        print(f"Days Overdue: {days_overdue}")
        print(f"Payment ID: {payment.id}")
        print(f"Payment Amount: {payment.amount}")
        print(f"Student Status: {student.status}")
        print("-" * 50)

print("\n=== SUMMARY ===")
overdue_count = 0
for payment in unpaid_payments:
    if payment.studentsession and payment.studentsession.student.status == 'Active':
        days_diff = (payment.date - date.today()).days
        if days_diff < 0:  # Overdue
            overdue_count += 1

print(f"Total overdue unpaid payments: {overdue_count}")