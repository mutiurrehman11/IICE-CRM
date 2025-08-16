from django.db import models

# Create your models here.

class StudentFee(models.Model):
    student = models.ForeignKey('Admin.Student', on_delete=models.CASCADE, related_name='moderator_fees')
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_fee = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installments_count = models.PositiveSmallIntegerField(default=0)
    per_installment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} Fee: {self.final_fee}"

class Installment(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')

    def __str__(self):
        return f"{self.student_fee.student} Installment {self.installment_number}: {self.amount} ({self.status})"
