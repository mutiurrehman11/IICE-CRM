#!/usr/bin/env python
"""
Test script to verify email configuration with SSL settings
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IICE.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import time

def test_email_with_retry():
    """
    Test email sending with retry logic
    """
    print("Testing email configuration...")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Use SSL: {settings.EMAIL_USE_SSL}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"Email Timeout: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')}")
    print("-" * 50)
    
    # Test email details - using the same email as sender for testing
    test_email = settings.EMAIL_HOST_USER  # Send to self for testing
    subject = "Test Email - IICE CRM System"
    message = """This is a test email to verify the email configuration.
    
If you receive this email, the configuration is working correctly.
    
Timestamp: {}
Configuration: TLS Port 587
From: IICE CRM System
    """.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    
    print(f"Sending test email to: {test_email}")
    
    # Retry logic
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Sending test email...")
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            print("✅ Email sent successfully!")
            print(f"Test email sent to: {test_email}")
            print("\n🎉 Email configuration is working correctly!")
            print("\nNext steps:")
            print("1. Check the inbox of", test_email)
            print("2. The fee reminder system should now work properly")
            print("3. Try sending a fee reminder from the admin panel")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt + 1} failed: {error_msg}")
            
            if 'WinError 10060' in error_msg:
                print("   → Connection timeout detected")
                print("   → This could be due to:")
                print("     - Windows Firewall blocking outbound SMTP")
                print("     - Antivirus software blocking email")
                print("     - ISP blocking SMTP ports")
                print("     - Network connectivity issues")
            elif 'Authentication failed' in error_msg:
                print("   → Authentication issue - check email credentials")
            elif 'Connection refused' in error_msg:
                print("   → Connection refused - check port and SSL settings")
            elif 'SMTPAuthenticationError' in error_msg:
                print("   → Gmail App Password might be incorrect")
                print("   → Make sure 2-Factor Authentication is enabled")
            
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"   → Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("\n❌ All attempts failed!")
                print("\n🔧 Troubleshooting steps:")
                print("1. Check Windows Firewall:")
                print("   - Go to Windows Defender Firewall")
                print("   - Allow Python through firewall")
                print("   - Allow outbound connections on port 587")
                print("\n2. Check Antivirus settings:")
                print("   - Temporarily disable email protection")
                print("   - Add Python to antivirus exceptions")
                print("\n3. Try alternative solutions:")
                print("   - Use mobile hotspot to test network")
                print("   - Contact ISP about SMTP port blocking")
                print("   - Consider using console backend for testing")
                return False
    
    return False

def test_console_backend():
    """
    Test with console backend (emails print to console)
    """
    print("\n" + "=" * 50)
    print("Testing with Console Backend (for debugging)")
    print("=" * 50)
    
    # Temporarily change to console backend
    original_backend = settings.EMAIL_BACKEND
    settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    try:
        send_mail(
            subject="Test Email - Console Backend",
            message="This email should appear in the console output.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["test@example.com"],
            fail_silently=False,
        )
        print("\n✅ Console backend test successful!")
        print("This confirms Django email functionality is working.")
        print("The issue is specifically with SMTP connectivity.")
    except Exception as e:
        print(f"❌ Console backend test failed: {e}")
    finally:
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend

if __name__ == "__main__":
    print("IICE CRM Email Configuration Test")
    print("=" * 50)
    
    success = test_email_with_retry()
    
    if not success:
        print("\n" + "=" * 50)
        print("Since SMTP failed, testing console backend...")
        test_console_backend()
        
        print("\n💡 Temporary Solution:")
        print("If SMTP continues to fail, you can temporarily use console backend:")
        print("1. In settings.py, change EMAIL_BACKEND to:")
        print("   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")
        print("2. Emails will print to the Django console instead of sending")
        print("3. This allows you to test the reminder functionality")
        print("4. Switch back to SMTP when connectivity is resolved")