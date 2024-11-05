import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control

from authentication.models import User
from Admin import models as admin_models
from .forms import UserForm, SessionForm, StudentForm, LeadForm

def StudentSession(request, studentid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    userdata = admin_models.Student.objects.get(id=studentid)
    sessions = admin_models.StudentSession.objects.filter(student=userdata)

    context = {
        'user': user,
        'userdata': userdata,
        'sessions': sessions,
    }
    return render(request, 'Admin/StudentSession.html', context)
def LeadView(request, leadid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    userdata = admin_models.Lead.objects.get(id=leadid)  # The user you are trying to update

    context = {
        'user': user,
        'userdata': userdata,
    }

    if request.method == 'POST':
        form = LeadForm(request.POST, request.FILES, instance=userdata)  # Form for 'userdata'

        if form.is_valid():
            form.save()
            return redirect('LeadView', leadid=leadid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = LeadForm(instance=userdata)

    context['form'] = form
    return render(request, 'Admin/LeadView.html', context)
def DeleteLead(request, leadid):
    if 'user_id' not in request.session:
        return redirect('home')
    admin_models.Lead.objects.get(id=leadid).delete()
    return redirect('Leads')
def AddLead(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user

    if request.method == 'POST':
        form = LeadForm(request.POST)

        if form.is_valid():
            newuser = form.save(commit=False)
            newuser.save()  # Save the new user

            messages.success(request, "Lead added successfully!")
            return redirect('Leads')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = LeadForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Admin/AddLead.html', context)
def Leads(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    Leads = admin_models.Lead.objects.all()
    context = {
        'user': user,
        'Leads': Leads,
    }
    return render(request, 'Admin/Leads.html', context)
def DeleteStudent(request, studentid):
    if 'user_id' not in request.session:
        return redirect('home')
    admin_models.Student.objects.get(id=studentid).delete()
    return redirect('Students')
def StudentView(request, studentid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    userdata = admin_models.Student.objects.get(id=studentid)  # The user you are trying to update
    status_choices = admin_models.Student.STATUS_CHOICES

    context = {
        'user': user,
        'userdata': userdata,
        'status_choices': status_choices,
    }

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=userdata)  # Form for 'userdata'

        if form.is_valid():
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                if userdata.profile_photo:
                    print(f"Old profile photo path: {userdata.profile_photo.path}")
                    if os.path.exists(userdata.profile_photo.path):
                        os.remove(userdata.profile_photo.path)

                userdata.profile_photo = request.FILES['profile_photo']
            if 'cnic_photo' in request.FILES:
                if userdata.cnic_photo:
                    print(f"Old profile photo path: {userdata.cnic_photo.path}")
                    if os.path.exists(userdata.cnic_photo.path):
                        os.remove(userdata.cnic_photo.path)

                userdata.cnic_photo = request.FILES['cnic_photo']
            if 'degree_photo' in request.FILES:
                if userdata.degree_photo:
                    print(f"Old profile photo path: {userdata.degree_photo.path}")
                    if os.path.exists(userdata.degree_photo.path):
                        os.remove(userdata.degree_photo.path)

                userdata.degree_photo = request.FILES['degree_photo']
                    # Save user changes
            form.save()
            return redirect('StudentView', studentid=studentid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = StudentForm(instance=userdata)

    context['form'] = form
    return render(request, 'Admin/StudentView.html', context)
def ExStudents(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    students = admin_models.Student.objects.filter(status="Inactive")
    context = {
        'user': user,
        'students': students,
    }
    return render(request, 'Admin/ExStudents.html', context)
def AddStudent(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    print(user)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            newuser = form.save(commit=False)

            # Handle profile photo if uploaded
            if 'profile_photo' in request.FILES:
                newuser.profile_photo = request.FILES['profile_photo']
            if 'cnic_photo' in request.FILES:
                newuser.cnic_photo = request.FILES['cnic_photo']
            if 'degree_photo' in request.FILES:
                newuser.degree_photo = request.FILES['degree_photo']

            newuser.save()  # Save the new user

            messages.success(request, "Student added successfully!")
            return redirect('Students')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = StudentForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Admin/AddStudent.html', context)
def Students(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    students = admin_models.Student.objects.filter(status="Active")
    context = {
        'user': user,
        'students': students,
    }
    return render(request, 'Admin/Students.html', context)
def DeleteSession(request, sessionid):
    if 'user_id' not in request.session:
        return redirect('home')
    admin_models.Sessions.objects.get(id=sessionid).delete()
    return redirect('Sessions')
def CompletedSessions(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    sessions = admin_models.Sessions.objects.filter(status="Inactive")
    context = {
        'user': user,
        'sessions': sessions,
    }
    return render(request, 'Admin/CompletedSessions.html', context)
def AddSession(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user

    if request.method == 'POST':
        form = SessionForm(request.POST,request.FILES)

        if form.is_valid():
            newsession = form.save(commit=False)
            newsession.save()  # Save the new user

            messages.success(request, "User added successfully!")
            return redirect('Sessions')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = UserForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Admin/AddSession.html', context)
def SessionView(request, sessionid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    sessiondata = admin_models.Sessions.objects.get(id=sessionid)  # The user you are trying to update

    status_choices = admin_models.Sessions.STATUS_CHOICES

    context = {
        'user': user,
        'sessiondata': sessiondata,
        'status_choices': status_choices,
    }

    if request.method == 'POST':
        form = SessionForm(request.POST, request.FILES, instance=sessiondata)  # Form for 'userdata'

        if form.is_valid():
            form.save()
            return redirect('SessionView', sessionid=sessionid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = SessionForm(instance=sessiondata)

    context['form'] = form

    return render(request, 'Admin/SessionView.html', context)
def Sessions(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    sessions = admin_models.Sessions.objects.filter(status="Active")
    context = {
        'user': user,
        'sessions': sessions,
    }
    return render(request, 'Admin/Sessions.html', context)
def DeleteFaculty(request, userid):
    if 'user_id' not in request.session:
        return redirect('home')
    User.objects.get(id=userid).delete()
    return redirect('Faculty')
def AddFaculty(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            newuser = form.save(commit=False)

            # Handle profile photo if uploaded
            if 'profile_photo' in request.FILES:
                newuser.profile_photo = request.FILES['profile_photo']

            newuser.save()  # Save the new user

            messages.success(request, "User added successfully!")
            return redirect('Faculty')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = UserForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Admin/AddFaculty.html', context)
def FacultyView(request, userid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    userdata = User.objects.get(id=userid)  # The user you are trying to update

    usertype_choices = User.USER_TYPE_CHOICES
    status_choices = User.STATUS_CHOICES

    context = {
        'user': user,
        'userdata': userdata,
        'usertype_choices': usertype_choices,
        'status_choices': status_choices,
    }

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=userdata)  # Form for 'userdata'

        if form.is_valid():
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                if userdata.profile_photo:
                    print(f"Old profile photo path: {userdata.profile_photo.path}")
                    if os.path.exists(userdata.profile_photo.path):
                        os.remove(userdata.profile_photo.path)

                userdata.profile_photo = request.FILES['profile_photo']

            # Save user changes
            form.save()
            return redirect('FacultyView', userid=userid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = UserForm(instance=userdata)

    context['form'] = form

    return render(request, 'Admin/FacultyView.html', context)
def Faculty(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    users = User.objects.all()
    context = {
        'user': user,
        'users': users,
    }
    return render(request, 'Admin/Faculty.html', context)
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
            return redirect('Admin_Profile')  # Redirect to avoid form resubmission

    else:
        form = UserForm(instance=user)  # Pre-populate form with user data

    return render(request, 'Admin/Profile.html', {'form': form, 'user': user})
def Logout(request):
    request.session.flush()  # This clears all session data

    # Redirect to login page after logout
    return redirect('home')
def Admin_Dashboard(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    users = User.objects.all()
    context = {
        'user': user,
        'users': users,
    }
    return render(request, 'Admin/Dashboard.html',context)
