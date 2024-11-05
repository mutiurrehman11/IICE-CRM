from django.contrib import admin

from .models import Sessions,Student,Lead, StudentSession

admin.site.register(Sessions)
admin.site.register(Student)
admin.site.register(Lead)
admin.site.register(StudentSession)
