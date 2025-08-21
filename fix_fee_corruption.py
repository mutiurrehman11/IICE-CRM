from django.core.management.base import BaseCommand
from Admin.models import StudentSession

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Reset all StudentSession.fee to their original session.fee values
        corrupted_sessions = StudentSession.objects.all()
        
        for session in corrupted_sessions:
            original_fee = session.session.fee
            if session.fee != original_fee:
                print(f"Fixing session {session.id}: {session.fee} -> {original_fee}")
                session.fee = original_fee
                session.save()
        
        print("Fee corruption cleanup completed!")