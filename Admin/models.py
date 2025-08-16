import os
from django.db import models
from django.utils.text import slugify
from authentication.models import User
from django.utils import timezone

def student_profile_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename

def student_cnic_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename

def student_degree_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.student_name)}_{slugify(instance.email)}.{extension}"
    return filename

def session_photo_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{slugify(instance.session_name)}.{extension}"
    return filename

class Student(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    INACTIVE_REASON_CHOICES = [
        ('Freeze', 'Freeze'),
        ('Expelled', 'Expelled'),
        ('', 'None'),
    ]
    rollno = models.CharField(max_length=100, blank=True, null=True, unique=True)
    student_name = models.CharField(max_length=50,blank=True, null=True)
    father_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(unique=True,blank=True, null=True)
    cnic = models.CharField(max_length=15,blank=True, null=True)
    profile_photo = models.ImageField(upload_to=student_profile_photo_path, blank=True, null=True)
    cnic_photo = models.ImageField(upload_to=student_cnic_photo_path, blank=True, null=True)
    degree_photo = models.ImageField(upload_to=student_degree_photo_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    inactive_reason = models.CharField(max_length=10, choices=INACTIVE_REASON_CHOICES, default='', blank=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    last_degree = models.CharField(max_length=50,blank=True, null=True)
    last_institution = models.CharField(max_length=50,blank=True, null=True)
    Temp_address = models.TextField(blank=True, null=True)
    Perm_address = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_students')
    created_at = models.DateTimeField(default=timezone.now)

    def generate_roll_number(self, session):
        """Generate roll number based on session name prefix"""
        # Session name to prefix mapping
        session_prefixes = {
            'CSS': 'CP',
            'CSS PMS': 'CP', 
            'PPSC': 'PF',
            'FPSC': 'PF',
            'PMS MINISTERIAL': 'PM',
            'PMS Ministerial': 'PM',
            'O LEVEL': 'O',
            'O Level': 'O',
            'A LEVEL': 'A', 
            'A Level': 'A',
            'IELTS': 'IE',
            'CADET COLLEGE': 'CC',
            'Cadet College': 'CC',
            'PTE': 'PTE',
            'URDU': 'U',
            'MATH': 'M',
            'ISLAMIAT': 'I'
        }
        
        # Get prefix based on session name
        session_name_upper = session.session_name.upper()
        prefix = None
        
        # Find matching prefix
        for key, value in session_prefixes.items():
            if key in session_name_upper:
                prefix = value
                break
        
        # If no specific prefix found, use first 2 letters of session name
        if not prefix:
            prefix = session.session_name[:2].upper()
        
        # Get the next number for this session
        existing_students = StudentSession.objects.filter(
            session=session
        ).order_by('id')
        
        next_number = existing_students.count() + 1
        
        # Generate roll number
        roll_number = f"{prefix}-{next_number:02d}"
        
        # Ensure uniqueness
        while Student.objects.filter(rollno=roll_number).exists():
            next_number += 1
            roll_number = f"{prefix}-{next_number:02d}"
            
        return roll_number

    @property
    def total_paid(self):
        """Calculate total amount paid by this student from Payments table"""
        return sum(
            payment.amount or 0 
            for session in self.student_sessions.all() 
            for payment in session.student_payments.all()
        )

    @property
    def total_fee(self):
        """Calculate total fee for all active sessions"""
        return sum(
            (session.fee or 0) + (session.registration_fee or 0) - (session.discount or 0)
            for session in self.student_sessions.filter(status='Active')
        )

    @property
    def remaining_balance(self):
        """Calculate remaining balance"""
        return max(0, self.total_fee - self.total_paid)

    @property
    def payment_status(self):
        """Get payment status: Paid, Partial, or Unpaid"""
        if self.remaining_balance <= 0:
            return 'Paid'
        elif self.total_paid > 0:
            return 'Partial'
        else:
            return 'Unpaid'

    def __str__(self):
        return f"{self.student_name} ({self.rollno})"

class Sessions(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    SESSION_TYPE_CHOICES = [
        ('time_period', 'Time Period Session'),
        ('monthly', 'Monthly Session'),
    ]
    
    session_name = models.CharField(max_length=50)
    session_type = models.CharField(max_length=15, choices=SESSION_TYPE_CHOICES, default='time_period')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    session_photo = models.ImageField(upload_to=session_photo_path, blank=True, null=True)
    registration_fee = models.IntegerField()
    fee = models.IntegerField(null=True, blank=True, help_text="Fee for all session types")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.fee:
            raise ValidationError({'fee': 'Fee is required for all sessions.'})

    def __str__(self):
        return f"{self.session_name} ({self.get_session_type_display()})"

class StudentSession(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_sessions')
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name='session_students')
    registration_date = models.DateField(null=True, blank=True)
    registration_fee = models.IntegerField(null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)  # ADD THIS LINE
    # fee_paid removed - now calculated from Payments table via session_paid property
    due_date = models.DateField(null=True, blank=True)
    next_monthly_due = models.DateField(null=True, blank=True)  # For monthly sessions
    discount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate roll number when creating new student session
        if not self.student.rollno:
            self.student.rollno = self.student.generate_roll_number(self.session)
            self.student.save()
            
        # Set fee from session
        self.fee = self.session.fee
        
        # Set next monthly due date for monthly sessions
        if self.session.session_type == 'monthly' and not self.next_monthly_due and self.registration_date:
            from datetime import timedelta
            self.next_monthly_due = self.registration_date + timedelta(days=30)
            
        super().save(*args, **kwargs)

    @property
    def session_paid(self):
        """Calculate amount paid for this specific session from Payments table"""
        return sum(payment.amount or 0 for payment in self.student_payments.all())

    @property
    def session_balance(self):
        """Calculate remaining balance for this session"""
        total_fee = (self.fee or 0) + (self.registration_fee or 0) - (self.discount or 0)
        return max(0, total_fee - self.session_paid)

    @property
    def session_total_fee(self):
        """Calculate total fee for this session"""
        return (self.fee or 0) + (self.registration_fee or 0) - (self.discount or 0)

    def __str__(self):
        return f"{self.student} - {self.session}"


class Lead(models.Model):
    INQUIRY_CHOICES = [
        ('Call', 'Call'),
        ('Message', 'Message'),
        ('Physical Visit', 'Physical Visit'),
    ]
    
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=True, null=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    area_of_residence = models.CharField(max_length=100, blank=True, null=True)
    session = models.ForeignKey(Sessions, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    form_of_inquiry = models.CharField(max_length=20, choices=INQUIRY_CHOICES, default='Call')

    def __str__(self):
        return f"{self.name}"

class Payments(models.Model):
    studentsession = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='student_payments')
    user = models.ForeignKey(User,on_delete=models.CASCADE ,related_name='payments')
    amount = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    course = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

class Notification(models.Model):
    CATEGORIES = [
        ('General', 'General'),
        ('Late Fee', 'Late fee'),
        ('New Entry', 'New Entry'),
        ('Deletion', 'Deletion'),
        ('New Fee', 'New Fee'),
        ('Updation', 'Updation'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    date = models.DateTimeField(auto_now_add=True)  # Changed from DateField to DateTimeField with auto_now_add
    category = models.CharField(max_length=10, choices=CATEGORIES)
    content = models.TextField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)  # Add this line

# StudentFee and Installment models removed - replaced by unified Payments system
# All payment data now calculated from Payments table using Student and StudentSession properties