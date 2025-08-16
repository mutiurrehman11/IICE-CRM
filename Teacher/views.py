from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import User
from Admin import models as admin_models
from datetime import date
from Admin.forms import UserForm, SessionForm, StudentForm, LeadForm
import os

def select_course(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    courses = admin_models.Sessions.objects.all()
    context = {
        'user': user,
        'courses': courses
    }
    return render(request, 'Teacher/Attendance.html', context)
def mark_attendance(request, course_id):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    course = admin_models.Sessions.objects.get(id=course_id)
    students = admin_models.StudentSession.objects.filter(session=course)

    if request.method == 'POST':
        date1 = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'status_{student.student.id}')
            admin_models.Attendance.objects.update_or_create(
                course=course,
                student=student.student,
                date=date1,
                defaults={'status': status}
            )
            sessions = admin_models.StudentSession.objects.filter(student=student.student)
            for session in sessions:
                if session.due_date and session.due_date < date.today():
                    message = "Due Date passed for " + student.student.student_name + " in " + session.session.session_name + " session"
                    admin_models.Notification.objects.create(user=user, date=date.today(), category='Late fee',
                                                             content=message)
        messages.success(request, 'Attendance marked successfully!')
        return redirect('tec_select_course')
    context = {
        'user': user,
        'course': course,
        'students': students
    }
    return render(request, 'Teacher/Mark_Attendance.html', context)

def Profile(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                if user.profile_photo:
                    print(user.profile_photo.path)
                    # Delete old photo if it exists
                    if os.path.exists(user.profile_photo.path):
                        os.remove(user.profile_photo.path)

                # Save the new photo
                user.profile_photo = request.FILES['profile_photo']

            # Save user changes
            form.save()
            return redirect('Teacher_Profile')  # Redirect to avoid form resubmission

    else:
        form = UserForm(instance=user)  # Pre-populate form with user data

    return render(request, 'Teacher/Profile.html', {'form': form, 'user': user})
