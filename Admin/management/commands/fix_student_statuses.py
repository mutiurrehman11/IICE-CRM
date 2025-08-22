from django.core.management.base import BaseCommand
from Admin.models import Sessions, StudentSession, Student

class Command(BaseCommand):
    help = 'Fix student statuses for completed sessions'

    def handle(self, *args, **options):
        # Find all completed sessions
        completed_sessions = Sessions.objects.filter(status='Completed')
        
        self.stdout.write(f'Found {completed_sessions.count()} completed sessions')
        
        total_students_updated = 0
        
        for session in completed_sessions:
            self.stdout.write(f'\nProcessing session: {session.session_name}')
            
            # Find all student sessions for this completed session
            student_sessions = StudentSession.objects.filter(session=session)
            
            for student_session in student_sessions:
                student = student_session.student
                
                self.stdout.write(
                    f'  Student: {student.student_name} - '
                    f'StudentSession status: {student_session.status}, '
                    f'Student status: {student.status}'
                )
                
                # Update student session status to Completed if not already
                if student_session.status != 'Completed':
                    student_session.status = 'Completed'
                    student_session.save()
                    self.stdout.write(f'    Updated StudentSession to Completed')
                
                # Update student status to Completed if not already
                if student.status != 'Completed':
                    student.status = 'Completed'
                    student.save()
                    total_students_updated += 1
                    self.stdout.write(f'    Updated Student to Completed (Ex-Student)')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully updated {total_students_updated} students to Ex-Student status'
            )
        )