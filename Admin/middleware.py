from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import Sessions, Notification
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class SessionStatusMiddleware(MiddlewareMixin):
    """
    Middleware to automatically update expired session statuses to 'Completed'.
    This runs on every request to ensure sessions are updated in real-time.
    """
    
    def process_request(self, request):
        """
        Check for expired sessions and update their status to 'Completed'.
        This runs before the view is processed.
        """
        try:
            # Get current date
            current_date = timezone.now().date()
            
            # Find all active sessions that have passed their end date
            expired_sessions = Sessions.objects.filter(
                status='Active',
                end_date__lt=current_date
            )
            
            if expired_sessions.exists():
                # Count how many sessions will be updated
                session_count = expired_sessions.count()
                session_names = list(expired_sessions.values_list('session_name', flat=True))
                
                # Update expired sessions and associated students
                total_students_updated = 0
                
                for session in expired_sessions:
                    # Update session status to Completed
                    session.status = 'Completed'
                    session.save()
                    
                    # Update all students associated with this session to 'Completed' status (Ex-Student)
                    from .models import StudentSession, Student
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
                    
                    total_students_updated += students_updated
                
                if session_count > 0:
                    logger.info(f"Automatically completed {session_count} expired sessions: {', '.join(session_names)} - {total_students_updated} students updated to Ex-Student status")
                    
                    # Create a notification for the superuser about the automatic completion
                    try:
                        superuser = User.objects.filter(is_superuser=True).first()
                        if superuser:
                            notification_message = (
                                f"System automatically completed {session_count} expired session(s): "
                                f"{', '.join(session_names[:3])}"  # Show first 3 session names
                            )
                            if len(session_names) > 3:
                                notification_message += f" and {len(session_names) - 3} more"
                            notification_message += f". {total_students_updated} students updated to Ex-Student status."
                            
                            Notification.objects.create(
                                user=superuser,
                                category='General',
                                content=notification_message,
                                is_read=False
                            )
                    except Exception as e:
                        logger.error(f"Failed to create notification for session completion: {e}")
                        
        except Exception as e:
            # Log the error but don't break the request flow
            logger.error(f"Error in SessionStatusMiddleware: {e}")
        
        # Continue with the request processing
        return None