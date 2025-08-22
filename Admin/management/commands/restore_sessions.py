from django.core.management.base import BaseCommand
from django.utils import timezone
from Admin.models import Sessions, Notification, StudentSession, Student
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Restore completed sessions back to active status and transition associated students back to current student status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session-ids',
            nargs='+',
            type=int,
            help='Specific session IDs to restore (space-separated)'
        )
        parser.add_argument(
            '--all-completed',
            action='store_true',
            help='Restore all completed sessions'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be restored without making changes'
        )

    def handle(self, *args, **options):
        if options['session_ids']:
            # Restore specific sessions by ID
            sessions_to_restore = Sessions.objects.filter(
                id__in=options['session_ids'],
                status='Completed'
            )
        elif options['all_completed']:
            # Restore all completed sessions
            sessions_to_restore = Sessions.objects.filter(status='Completed')
        else:
            self.stdout.write(
                self.style.ERROR('Please specify either --session-ids or --all-completed')
            )
            return

        if not sessions_to_restore.exists():
            self.stdout.write(
                self.style.WARNING('No completed sessions found to restore.')
            )
            return

        restored_count = 0
        total_students_updated = 0

        self.stdout.write(
            self.style.SUCCESS(f'Found {sessions_to_restore.count()} completed sessions to restore:')
        )

        for session in sessions_to_restore:
            self.stdout.write(f'\nProcessing session: {session.session_name} (ID: {session.id})')
            
            # Find all student sessions for this completed session
            student_sessions = StudentSession.objects.filter(session=session, status='Completed')
            students_in_session = student_sessions.count()
            
            self.stdout.write(f'  - Found {students_in_session} students to restore')
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'  - DRY RUN: Would restore session "{session.session_name}" and {students_in_session} students')
                )
                continue
            
            # Update session status to Active
            session.status = 'Active'
            session.save()
            
            students_updated = 0
            
            for student_session in student_sessions:
                # Update the student session status
                student_session.status = 'Active'
                student_session.save()
                
                # Update the student's overall status to 'Active' (Current Student)
                student = student_session.student
                student.status = 'Active'
                student.save()
                students_updated += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'    - Restored student {student.student_name} to Current Student status')
                )
            
            total_students_updated += students_updated
            restored_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'  - Successfully restored session "{session.session_name}" with {students_updated} students')
            )
            
            # Create system notification
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    Notification.objects.create(
                        user=admin_user,
                        category='Updation',
                        content=f'Management Command: Restored session "{session.session_name}" with {students_updated} students transitioned back to Current Student status'
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  - Could not create notification: {str(e)}')
                )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN COMPLETE: Would have restored {sessions_to_restore.count()} sessions')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSUCCESS: Restored {restored_count} sessions with {total_students_updated} total students transitioned back to Current Student status')
            )