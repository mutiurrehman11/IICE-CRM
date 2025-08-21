from django.core.management.base import BaseCommand
from django.utils import timezone
from Admin.models import Sessions, Notification, StudentSession, Student
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Automatically transition sessions to Completed status that have passed their end date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Find all active sessions that have passed their end date
        expired_sessions = Sessions.objects.filter(
            status='Active',
            end_date__lt=today
        )
        
        completed_count = 0
        total_students_updated = 0
        
        for session in expired_sessions:
            # Update session status to Completed
            session.status = 'Completed'
            session.save()
            
            # Update all students associated with this session to 'Completed' status (Ex-Student)
            student_sessions = StudentSession.objects.filter(session=session, status='Active')
            students_updated = 0
            
            for student_session in student_sessions:
                # Update the student session status
                student_session.status = 'Completed'
                student_session.save()
                
                # Update the student's overall status to 'Completed' (Ex-Student)
                student = student_session.student
                student.status = 'Completed'
                student.save()
                students_updated += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'  - Updated student {student.name} to Ex-Student status')
                )
            
            total_students_updated += students_updated
            
            # Create a notification for the superuser about the completion
            try:
                superuser = User.objects.filter(is_superuser=True).first()
                if superuser:
                    notification_content = f"System automatically completed expired session: {session.session_name} (ended on {session.end_date})"
                    if students_updated > 0:
                        notification_content += f". {students_updated} students updated to Ex-Student status."
                    
                    Notification.objects.create(
                        user=superuser,
                        category='General',
                        content=notification_content,
                        is_read=False
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not create notification for session {session.session_name}: {e}')
                )
            
            completed_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Completed session: {session.session_name} (ended on {session.end_date}) - {students_updated} students updated')
            )
        
        if completed_count == 0:
            self.stdout.write(self.style.SUCCESS('No expired sessions found.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully completed {completed_count} expired session(s) and updated {total_students_updated} students to Ex-Student status.')
            )