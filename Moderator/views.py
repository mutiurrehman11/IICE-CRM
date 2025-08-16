import os
from lib2to3.fixes.fix_input import context
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import User
from Admin import models as admin_models
from Admin.forms import UserForm, SessionForm, StudentForm, LeadForm
from datetime import date


def MakeNotification(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    sessions = admin_models.StudentSession.objects.all()
    for session in sessions:
        if session.due_date < date.today():
            message = "Due Date passed for " + session.student.student_name + " in " + session.session.session_name + " session"
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Late fee',
                                                     content=message)

    notifications = admin_models.Notification.objects.all().order_by('-date')
    context = {
        'user': user,
        'notifications': notifications
    }
    return render(request, 'Moderator/Notifications.html', context)
def Notification(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    notifications = admin_models.Notification.objects.filter(category="Late fee").order_by('-date')
    context = {
        'user': user,
        'notifications': notifications
    }
    return render(request, 'Moderator/Notifications.html', context)
def DeleteStudentSession(request, studentsessionid):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    studentsession = admin_models.StudentSession.objects.get(id=studentsessionid)
    studentid = studentsession.student.id
    message = "Removed  " + studentsession.student.student_name + " from " + studentsession.session.session_name + " session"
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    studentsession.delete()
    return redirect('mod_StudentSession', studentid=studentid)
def StudentSessionView(request, studentsessionid):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    userdata = admin_models.StudentSession.objects.get(id=studentsessionid)  # The user you are trying to update

    context = {
        'user': user,
        'userdata': userdata,
    }

    if request.method == 'POST':
        userdata.status = request.POST.get('status')
        userdata.notes = request.POST.get('notes')
        userdata.due_date = request.POST.get('due_date')
        message = "Updated  " + userdata.student.student_name + " Record in " + userdata.session.session_name + " session"
        admin_models.Notification.objects.create(user=user, date=date.today(), category='Updation', content=message)
        userdata.save()

    return render(request, 'Moderator/StudentSessionView.html', context)
def AddStudentSession(request, studentid):
    if 'user_id' not in request.session:
        return redirect('home')
    # Get the student object
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    student =  admin_models.Student.objects.get(id=studentid)
    active_sessions = admin_models.Sessions.objects.filter(status='Active')  # Fetch active sessions

    if request.method == 'POST':
        # Get form data
        session_id = request.POST.get('session_id')
        registration_fee = request.POST.get('registration_fee')
        fee = request.POST.get('fee')
        due_date = request.POST.get('due_date')
        discount = request.POST.get('discount', 0)  # Default to 0 if no discount is provided
        notes = request.POST.get('notes', '')

        # Fetch the selected session object
        session = admin_models.Sessions.objects.get(id=session_id)

        # Create a new StudentSession instance
        student_session = admin_models.StudentSession(
            student=student,
            session=session,
            registration_date=request.POST.get('registration_date'),  # Set registration date if needed
            registration_fee=registration_fee,
            fee=fee,
            due_date=due_date,
            discount=discount,
            fee_paid=0,
            status='Active',  # Set initial status as Active
            notes=notes,
        )

        # Save to the database
        student_session.save()

        message = "Added  " + student.student_name + " To " + session.session_name + " session"
        admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)

        # Redirect to the desired page (e.g., student session view)
        return redirect('mod_StudentSession', studentid=studentid)

    # Render the form with student and active sessions
    return render(request, 'Moderator/AddStudentSession.html', {
        'student': student,
        'active_sessions': active_sessions,
    })
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
        'studentid': studentid
    }
    return render(request, 'Moderator/StudentSession.html', context)
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
            message = "Updated  " + userdata.name + " Information in Leads"
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
            return redirect('mod_LeadView', leadid=leadid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = LeadForm(instance=userdata)

    context['form'] = form
    return render(request, 'Moderator/LeadView.html', context)
def DeleteLead(request, leadid):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    lead = admin_models.Lead.objects.get(id=leadid)
    message = "Removed  " + lead.name + " from Leads"
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    lead.delete()
    return redirect('mod_Leads')
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
            message = "Added  " + newuser.name + " to Leads"
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
            messages.success(request, "Lead added successfully!")
            return redirect('mod_Leads')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = LeadForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Moderator/AddLead.html', context)
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
    return render(request, 'Moderator/Leads.html', context)
def DeleteStudent(request, studentid):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    student = admin_models.Student.objects.get(id=studentid)
    if student.profile_photo:
        if os.path.exists(student.profile_photo.path):
            os.remove(student.profile_photo.path)
    if student.cnic_photo:
        if os.path.exists(student.cnic_photo.path):
            os.remove(student.cnic_photo.path)
    if student.degree_photo:
        if os.path.exists(student.degree_photo.path):
            os.remove(student.degree_photo.path)
    student.delete()
    message = "Removed  " + student.student_name
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    from_page = request.GET.get('from')
    if from_page == 'exstudents':
        return redirect('mod_ExStudents')  # Replace 'ExStudents' with the actual name of the ex-students page URL
    return redirect('mod_Students')
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
        'redirection': 1
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
            message = "Updated  " + userdata.student_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Updation', content=message)
            return redirect('mod_StudentView', studentid=studentid)  # Redirect to avoid resubmission
        else:
            # Print form errors for debugging
            print("Form is not valid:")
            print(form.errors)

    else:
        form = StudentForm(instance=userdata)

    context['form'] = form
    return render(request, 'Moderator/StudentView.html', context)
def ExStudents(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    students = admin_models.Student.objects.filter(status="Inactive")
    context = {
        'user': user,
        'students': students,
        'redirection': 2
    }
    return render(request, 'Moderator/ExStudents.html', context)
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
                
            # Set the moderator as the one who added this student
            newuser.added_by = user

            newuser.save()  # Save the new user

            # Handle multiple session selections (if present)
            selected_sessions = request.POST.getlist('sessions') if 'sessions' in request.POST else []
            total_fee = 0
            registration_fee = 0
            single_due_date_str = request.POST.get('single_due_date')
            single_due_date = None
            if single_due_date_str:
                from datetime import datetime
                single_due_date = datetime.strptime(single_due_date_str, '%Y-%m-%d').date()
            # Around line 347-355, uncomment the fee assignment:
            student_session = admin_models.StudentSession(
            student=newuser,
            session=session,
            registration_date=date.today(),
            registration_fee=session.registration_fee,
            fee=session.fee,  # ADD THIS LINE BACK
            status='Active',
            due_date=single_due_date if not request.POST.get('enable_installments') else None
            )
            student_session.save()
            total_fee += session.fee
            registration_fee += session.registration_fee

            # --- Fee Management Logic ---
            discount = float(request.POST.get('discount', 0))
            total_fee_with_reg = total_fee + registration_fee
            final_fee = float(request.POST.get('final_fee', total_fee_with_reg))
            paid_amount = float(request.POST.get('paid_amount', 0))
            enable_installments = request.POST.get('enable_installments') == 'on'
            installments_count = int(request.POST.get('installments_count') or 0)
            per_installment_amount = float(request.POST.get('per_installment_amount') or 0)
            latest_installment_paid = float(request.POST.get('latest_installment_paid') or 0)
            due_date_str = request.POST.get('due_date')
            from datetime import timedelta
            from django.utils import timezone
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date()

            # Create StudentFee record (Moderator model)
            from Moderator import models as mod_models
            student_fee = mod_models.StudentFee.objects.create(
                student=newuser,
                total_fee=total_fee_with_reg,
                discount=discount,
                final_fee=final_fee,
                paid_amount=paid_amount,
                installments_count=installments_count if enable_installments else 0,
                per_installment_amount=per_installment_amount if enable_installments else None
            )

            # Create Installment records if enabled
            if enable_installments and installments_count > 0:
                for i in range(1, installments_count + 1):
                    amount = per_installment_amount
                    paid_date = None
                    status = 'Unpaid'
                    if i == 1 and latest_installment_paid > 0:
                        amount = latest_installment_paid
                        paid_date = due_date
                        status = 'Paid'
                    mod_models.Installment.objects.create(
                        student_fee=student_fee,
                        installment_number=i,
                        amount=amount,
                        due_date=due_date,
                        paid_date=paid_date,
                        status=status
                    )
                    # Next due date is one month later
                    due_date = (due_date + timedelta(days=32)).replace(day=due_date.day)

            message = "Added  " + newuser.student_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
            return redirect('mod_Students')
        else:
            print(form.errors)  # Debug: print any form errors

    else:
        form = StudentForm()

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'Moderator/AddStudent.html', context)
def Students(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object
    students = admin_models.Student.objects.filter(status="Active")
    context = {
        'user': user,
        'students': students,
        'redirection': 1
    }
    return render(request, 'Moderator/Students.html', context)
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
            return redirect('Moderator_Profile')  # Redirect to avoid form resubmission

    else:
        form = UserForm(instance=user)  # Pre-populate form with user data

    return render(request, 'Moderator/Profile.html', {'form': form, 'user': user})
def Payments(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user

    from Moderator import models as mod_models
    student_fees = mod_models.StudentFee.objects.select_related('student').prefetch_related('installments').all()

    context = {
        'user': user,
        'student_fees': student_fees,
    }
    return render(request, 'Moderator/Payments.html', context)

