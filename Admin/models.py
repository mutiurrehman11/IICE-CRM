import os
from django.db import models
from django.utils.text import slugify
from authentication.models import User
from django.utils import timezone

def student_profile_photo_path(instance, filename):
    return f"student_profiles/{instance.rollno}/{filename}"

def student_cnic_photo_path(instance, filename):
    return f"student_cnic/{instance.rollno}/{filename}"

def student_degree_photo_path(instance, filename):
    return f"student_degrees/{instance.rollno}/{filename}"

def session_photo_path(instance, filename):
    return f"session_photos/{slugify(instance.session_name)}/{filename}"

class Student(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
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
        """Generate a unique roll number for the student in the given session"""
        # Get the session prefix (first 3 characters of session name)
        prefix = session.session_name[:3].upper()
        
        # Find the highest existing roll number for this session prefix
        existing_students = Student.objects.filter(
            rollno__startswith=prefix,
            student_sessions__session=session
        ).exclude(rollno__isnull=True).exclude(rollno='')
        
        # Extract numbers and find the next available
        existing_numbers = []
        for student in existing_students:
            try:
                # Extract number part after the prefix and dash
                number_part = student.rollno.split('-')[1]
                existing_numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue
        
        # Find next available number
        next_number = 1
        if existing_numbers:
            next_number = max(existing_numbers) + 1
        
        # Format roll number
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
        """Calculate total fee for all sessions (registration fee charged once)"""
        # Consider all sessions, not just active ones, to account for outstanding payments
        sessions_qs = self.student_sessions.all()
        
        # Sum of (fee - discount) across all sessions
        base_total = sum((s.fee or 0) - (s.discount or 0) for s in sessions_qs)
        
        # Determine primary session: earliest registration_date, fallback to lowest id
        primary_session = (
            sessions_qs.exclude(registration_date__isnull=True)
            .order_by('registration_date', 'id')
            .first()
            or sessions_qs.order_by('id').first()
        )
        
        one_time_reg_fee = 0
        if primary_session:
            one_time_reg_fee = (
                primary_session.registration_fee
                if primary_session.registration_fee is not None
                else (primary_session.session.registration_fee or 0)
            )
        
        return base_total + (one_time_reg_fee or 0)

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
        ('Completed', 'Completed'),
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
        ('Completed', 'Completed'),
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

    def clean(self):
        super().clean()
        
        # Validate: Prevent multiple active session enrollments
        if self.status == 'Active':
            existing_active = StudentSession.objects.filter(
                student=self.student,
                status='Active'
            ).exclude(pk=self.pk)
            
            if existing_active.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f'Student {self.student.student_name} is already enrolled in an active session: '
                    f'{existing_active.first().session.session_name}. '
                    f'Please complete or withdraw from the current session before enrolling in a new one.'
                )
    
    def save(self, *args, **kwargs):
        # Apply institutional policies before saving
        if not self.pk:  # New enrollment
            # Check for previous enrollments to apply fee waiver
            has_previous = StudentSession.objects.filter(student=self.student).exists()
            if has_previous and self.registration_fee is None:
                self.registration_fee = 0  # Waive registration fee for re-enrollments
                if not self.notes:
                    self.notes = ""
                self.notes += " [Registration fee waived - re-enrollment policy]"
        
        self.full_clean()  # This will call clean() method
        super().save(*args, **kwargs)

    @property
    def is_primary_session(self):
        """True if this is the student's primary session (earliest registration), else False"""
        sessions_qs = self.student.student_sessions.filter(status='Active')
        primary = (
            sessions_qs.exclude(registration_date__isnull=True)
            .order_by('registration_date', 'id')
            .first()
            or sessions_qs.order_by('id').first()
        )
        return primary and primary.id == self.id

    @property
    def session_paid(self):
        """Calculate amount paid for this specific session from Payments table"""
        return sum(payment.amount or 0 for payment in self.student_payments.all())

    @property
    def session_balance(self):
        """Calculate remaining balance for this session (registration fee only on primary session)"""
        reg_fee = 0
        if self.is_primary_session:
            reg_fee = (
                self.registration_fee
                if self.registration_fee is not None
                else (self.session.registration_fee or 0)
            )
        total_fee = (self.fee or 0) + reg_fee - (self.discount or 0)
        return max(0, total_fee - self.session_paid)

    @property
    def session_total_fee(self):
        """Calculate total fee for this session (registration fee only on primary session)"""
        reg_fee = 0
        if self.is_primary_session:
            reg_fee = (
                self.registration_fee
                if self.registration_fee is not None
                else (self.session.registration_fee or 0)
            )
        return (self.fee or 0) + reg_fee - (self.discount or 0)

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
        ('Monthly Renewal', 'Monthly Renewal'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    date = models.DateTimeField(auto_now_add=True)  # Changed from DateField to DateTimeField with auto_now_add
    category = models.CharField(max_length=20, choices=CATEGORIES)
    content = models.TextField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)  # Add this line

# StudentFee and Installment models removed - replaced by unified Payments system
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
# All payment data now calculated from Payments table using Student and StudentSession properties
#
