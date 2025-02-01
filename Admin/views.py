import os
from lib2to3.fixes.fix_input import context
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import User
from Admin import models as admin_models
from .forms import UserForm, SessionForm, StudentForm, LeadForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse
from django.core.mail import send_mail


def notify_late_fee_students(request):
    if request.method == 'POST':
        try:
            sessions = admin_models.StudentSession.objects.all()
            for session in sessions:
                if session.due_date < date.today():
                    print(session.student.student_name)
                    send_mail(
                        subject="Late Fee Notification",
                        message=f"Dear {session.student.student_name},\n\nPlease note that you have pending fees for {session.session.session_name}. Kindly pay them at the earliest.\n\nRegards,\nIqra Academy\nAccounts Department",
                        from_email="admin@iqrainstitute.com",
                        recipient_list=[session.student.email],
                    )
            return JsonResponse(
                {'status': 'success', 'message': 'Emails successfully sent to students with late fees.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
def EmailService(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    if request.method == 'POST':
        # Get data from the form
        email_content = request.POST.get('email_content')  # Email body
        email_subject = request.POST.get('email_subject')  # Email subject
        email_list = []
        if 'faculty_checkbox' in request.POST:
            selected_users = User.objects.all()
            email_addresses = [user.email for user in selected_users if user.email]
            email_list.extend(email_addresses)
        if 'student_checkbox' in request.POST:
            selected_users = admin_models.Student.objects.all()
            email_addresses = [user.email for user in selected_users if user.email]
            email_list.extend(email_addresses)
        if 'lead_checkbox' in request.POST:
            selected_users = admin_models.Lead.objects.all()
            email_addresses = [user.email for user in selected_users if user.email]
            email_list.extend(email_addresses)

        if email_list:
            try:
                # Send the email to the selected users
                send_mail(
                    subject=email_subject,
                    message=email_content,
                    from_email='callmemutiurrehman@gmail.com',  # Replace with your sender email
                    recipient_list=email_list,
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success', 'message': 'Emails sent successfully!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to send emails: {str(e)}'})

        return JsonResponse({'status': 'error', 'message': 'No valid email addresses found.'})
    context = {
        'user': user,
    }
    return render(request, 'Admin/EmailService.html', context)
def print_attendance_report(request, course_id):
    # Get the course object
    course = admin_models.Sessions.objects.get(id=course_id)

    # Fetch attendance data for this course
    attendances = admin_models.Attendance.objects.filter(course=course).order_by('date')
    students = admin_models.StudentSession.objects.filter(session=course)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{course.session_name}_attendance_report.pdf"'

    # Create the PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Add institution name
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(110, height - 70, "IQRA INSTITUTE OF COMPETITIVE EXAMINATION")  # Replace with your institution name

    # Add report title
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 120, f"Attendance Report for {course.session_name}")

    # Prepare the table data
    dates = sorted(set([attendance.date for attendance in attendances]))
    max_dates_per_table = 5
    table_data_chunks = [dates[i:i + max_dates_per_table] for i in range(0, len(dates), max_dates_per_table)]

    # Create each table for each chunk of dates
    current_y_position = height - 160  # Starting y position for the first table
    for table_data in table_data_chunks:
        # Create the table header (Student Name + Dates)
        table_data_with_header = [["Student Name"] + [str(date1) for date1 in table_data]]

        # Create the table rows with student attendance status for each date
        for student in students:
            row = [student.student.student_name]
            for date1 in table_data:
                attendance = attendances.filter(student=student.student, date=date1).first()
                status = attendance.status if attendance else "Absent"
                row.append(status)
            table_data_with_header.append(row)

        # Define table style
        table = Table(table_data_with_header, colWidths=[140] + [70 for _ in table_data])  # Adjust column widths
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Place the table on the PDF
        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, current_y_position)  # Adjust the position

        # Update the y position for the next table (leave space between tables)
        current_y_position -= (len(table_data_with_header) * 20 + 20)  # Adjust spacing if necessary

        # Check if more tables are needed and if current table exceeds the page height
        if current_y_position < 100:
            pdf.showPage()  # Create a new page if space is not enough
            current_y_position = height - 100  # Reset the y position for the new page

    # Finalize the PDF
    pdf.save()
    return response
def Payment(request):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    payments = admin_models.Payments.objects.all().order_by('-date')
    context = {
        'user': user,
        'payments': payments
    }
    return render(request, 'Admin/Payments.html', context)
@csrf_exempt
def add_fee_payment(request, session_id):
    if 'user_id' not in request.session:
        return redirect('home')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    if request.method == "POST":
        try:
            # Get the session and payment details
            session = admin_models.StudentSession.objects.get(id=session_id)
            amount = int(request.POST.get("amount"))
            due_date = request.POST.get("due_date")

            # Validate amount
            remaining_fee = session.fee - (session.fee_paid or 0)
            if amount <= 0 or amount > remaining_fee:
                return JsonResponse({"success": False, "error": "Invalid amount entered."})

            # Add the payment record
            payment = admin_models.Payments.objects.create(
                studentsession=session,
                user=user,  # Replace with the logged-in user
                amount=amount,
                date=date.today(),
            )

            # Update the session's fee_paid and due_date
            session.fee_paid = session.fee_paid + amount
            session.due_date = due_date
            session.save()
            message = "Collected Fee Rs " + str(amount) + " from " + session.student.student_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Fee' ,content=message)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})

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
    return render(request, 'Admin/Notifications.html', context)
def Notification(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    notifications = admin_models.Notification.objects.all().order_by('-date')
    context = {
        'user': user,
        'notifications': notifications
    }
    return render(request, 'Admin/Notifications.html', context)
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
    return render(request, 'Admin/Attendance.html', context)
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
                if session.due_date < date.today():
                    message = "Due Date passed for " + student.student.student_name + " in " + session.session.session_name + " session"
                    admin_models.Notification.objects.create(user=user, date=date.today(), category='Late fee',
                                                             content=message)
        messages.success(request, 'Attendance marked successfully!')
        return redirect('select_course')
    context = {
        'user': user,
        'course': course,
        'students': students
    }
    return render(request, 'Admin/Mark_Attendance.html', context)
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
    return redirect('StudentSession', studentid=studentid)
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

    return render(request, 'Admin/StudentSessionView.html', context)
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
        return redirect('StudentSession', studentid=studentid)

    # Render the form with student and active sessions
    return render(request, 'Admin/AddStudentSession.html', {
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
            message = "Updated  " + userdata.name + " Information in Leads"
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
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
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    lead = admin_models.Lead.objects.get(id=leadid)
    message = "Removed  " + lead.name + " from Leads"
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    lead.delete()
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
            message = "Added  " + newuser.name + " to Leads"
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
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
        return redirect('ExStudents')  # Replace 'ExStudents' with the actual name of the ex-students page URL
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
        'redirection': 2
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

            message = "Added  " + newuser.student_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
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
        'redirection': 1
    }
    return render(request, 'Admin/Students.html', context)
def DeleteSession(request, sessionid):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    session = admin_models.Sessions.objects.get(id=sessionid)
    if session.session_photo:
        if os.path.exists(session.session_photo.path):
            os.remove(session.session_photo.path)
    message = "Deleted Session: " + session.session_name
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    session.delete()
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

            message = "Added Session: " + newsession.session_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
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
def SessionStudentView(request, sessionid):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    sessiondata = admin_models.Sessions.objects.get(id=sessionid)
    students = admin_models.StudentSession.objects.filter(session=sessiondata)
    context = {
        'user': user,
        'sessiondata': sessiondata,
        'students': students,
    }
    return render(request, 'Admin/SessionStudentView.html', context)
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
            if 'session_photo' in request.FILES:
                if sessiondata.session_photo:
                    print(f"Old profile photo path: {sessiondata.session_photo.path}")
                    if os.path.exists(sessiondata.session_photo.path):
                        os.remove(sessiondata.session_photo.path)
            form.save()
            message = "Updated Session: " + sessiondata.session_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Updation', content=message)
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
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  # Logged-in user
    faculty = User.objects.get(id=userid)
    if faculty.profile_photo:
        if os.path.exists(faculty.profile_photo.path):
            os.remove(faculty.profile_photo.path)
    message = "Deleted Faculty: " + faculty.first_name + " " + faculty.last_name
    admin_models.Notification.objects.create(user=user, date=date.today(), category='Deletion', content=message)
    faculty.delete()
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

            message = "Added Faculty: " + newuser.first_name + " " + newuser.last_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='New Entry', content=message)
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
            message = "Updated Faculty: " + userdata.first_name + " " + userdata.last_name
            admin_models.Notification.objects.create(user=user, date=date.today(), category='Updation', content=message)
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
    total_students = admin_models.Student.objects.count()  # Total number of students
    total_leads = admin_models.Lead.objects.count()  # Total number of leads
    total_sessions = admin_models.Sessions.objects.count()
    total_users = User.objects.count()
    context = {
        'user': user,
        'users': users,
        'total_students': total_students,
        'total_leads': total_leads,
        'total_sessions': total_sessions,
        'total_users': total_users,
    }
    return render(request, 'Admin/Dashboard.html',context)
