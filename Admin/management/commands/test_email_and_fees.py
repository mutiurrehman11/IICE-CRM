from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from Admin.models import Student
from datetime import date

class Command(BaseCommand):
    help = 'Test email configuration and check students with pending fees'

    def handle(self, *args, **options):
        self.stdout.write("Testing email configuration...")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

        self.stdout.write("\nChecking students with pending fees...")
        students = Student.objects.filter(status='Active')
        self.stdout.write(f"Total active students: {students.count()}")

        students_with_pending = 0
        for student in students[:10]:  # Check first 10 students
            self.stdout.write(f"\nStudent: {student.student_name}")
            self.stdout.write(f"Email: {student.email or 'No email'}")
            self.stdout.write(f"Total Fee: Rs. {student.total_fee:,.0f}")
            self.stdout.write(f"Total Paid: Rs. {student.total_paid:,.0f}")
            self.stdout.write(f"Remaining Balance: Rs. {student.remaining_balance:,.0f}")
            self.stdout.write(f"Payment Status: {student.payment_status}")
            
            if student.remaining_balance > 0:
                students_with_pending += 1
                self.stdout.write("  *** HAS PENDING FEES ***")
            
            # Check sessions
            sessions = student.student_sessions.all()
            self.stdout.write(f"Sessions: {sessions.count()}")
            for session in sessions:
                self.stdout.write(f"  - {session.session.session_name} ({session.status}): Balance Rs. {session.session_balance:,.0f}")
                if hasattr(session, 'due_date') and session.due_date:
                    overdue = session.due_date < date.today()
                    self.stdout.write(f"    Due: {session.due_date} {'(OVERDUE)' if overdue else '(OK)'}")

        self.stdout.write(f"\nStudents with pending fees: {students_with_pending}")

        # Test email sending
        self.stdout.write("\nTesting email sending...")
        try:
            send_mail(
                subject='Test Email from IICE CRM',
                message='This is a test email to verify email configuration.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✓ Test email sent successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Email sending failed: {str(e)}"))
            if 'WinError 10060' in str(e):
                self.stdout.write(self.style.WARNING("This is a connection timeout error. Possible causes:"))
                self.stdout.write("  - Firewall blocking SMTP connections")
                self.stdout.write("  - Antivirus blocking email sending")
                self.stdout.write("  - Network restrictions")
                self.stdout.write("  - Gmail security settings")
                self.stdout.write("  - App password not configured correctly")