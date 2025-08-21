from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from Admin import models as admin_models
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Process monthly session renewals for students whose next payment is due within 7 days'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to check for due renewals (default: 7)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days_ahead']
        today = date.today()
        check_until_date = today + timedelta(days=days_ahead)
        
        self.stdout.write(f"Processing monthly renewals for dates up to {check_until_date}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
        
        # Get all active student sessions for monthly sessions
        monthly_student_sessions = admin_models.StudentSession.objects.filter(
            session__session_type='monthly',
            status='Active'
        ).select_related('student', 'session')
        
        processed_count = 0
        renewed_count = 0
        
        for student_session in monthly_student_sessions:
            try:
                # Check if renewal is needed
                renewal_needed, next_due_date = self._check_renewal_needed(
                    student_session, today, check_until_date
                )
                
                if renewal_needed:
                    self.stdout.write(
                        f"Processing renewal for {student_session.student.student_name} "
                        f"in {student_session.session.session_name} (due: {next_due_date})"
                    )
                    
                    if not dry_run:
                        success = self._create_monthly_renewal_payment(
                            student_session, next_due_date
                        )
                        if success:
                            renewed_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ Created renewal payment for {student_session.student.student_name}"
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"✗ Failed to create renewal payment for {student_session.student.student_name}"
                                )
                            )
                    else:
                        renewed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[DRY RUN] Would create renewal payment for {student_session.student.student_name}"
                            )
                        )
                    
                    processed_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing {student_session.student.student_name}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Processed {processed_count} students, "
                f"created {renewed_count} renewal payments."
            )
        )
    
    def _check_renewal_needed(self, student_session, today, check_until_date):
        """
        Check if a monthly session renewal is needed for this student.
        Returns (renewal_needed, next_due_date)
        """
        # Get the last payment for this student session
        last_payment = admin_models.Payments.objects.filter(
            studentsession=student_session
        ).order_by('-date').first()
        
        if not last_payment:
            # No payments yet, check registration date
            if student_session.registration_date:
                # Calculate next monthly due date from registration
                next_due = student_session.registration_date + relativedelta(months=1)
                return next_due <= check_until_date, next_due
            return False, None
        
        # Calculate next monthly due date from last payment
        next_due = last_payment.date + relativedelta(months=1)
        
        # Check if there's already an unpaid payment for this due date
        existing_unpaid = admin_models.Payments.objects.filter(
            studentsession=student_session,
            date=next_due,
            amount=0
        ).exists()
        
        if existing_unpaid:
            # Already has unpaid payment for this date
            return False, None
        
        # Check if renewal is due within the specified days
        return next_due <= check_until_date, next_due
    
    def _create_monthly_renewal_payment(self, student_session, due_date):
        """
        Create a new unpaid payment record for monthly session renewal.
        Excludes registration fee as it's only charged once.
        """
        try:
            # Get system user for automated processes
            system_user = User.objects.filter(is_superuser=True).first()
            if not system_user:
                system_user = User.objects.first()
            
            if not system_user:
                self.stdout.write(
                    self.style.ERROR("No user found to assign the payment to")
                )
                return False
            
            # Create unpaid payment record (amount=0 means unpaid)
            payment = admin_models.Payments.objects.create(
                studentsession=student_session,
                user=system_user,
                amount=0,  # Unpaid
                date=due_date
            )
            
            # Update next_monthly_due field
            student_session.next_monthly_due = due_date
            student_session.save()
            
            # Create notification
            message = (
                f"Monthly renewal due for {student_session.student.student_name} "
                f"in {student_session.session.session_name} - "
                f"Rs.{student_session.session.fee} due on {due_date}"
            )
            
            admin_models.Notification.objects.create(
                user=system_user,
                category='Monthly Renewal',
                content=message
            )
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error creating renewal payment: {str(e)}")
            )
            return False