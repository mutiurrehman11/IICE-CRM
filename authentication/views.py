from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import User

def Admin_Dashboard(request):

    return render(request, 'Admin/Dashboard.html')
def Moderator_Dashboard(request):
    return render(request, 'Admin/Dashboard.html')
def Teacher_Dashboard(request):
    return render(request, 'Admin/Dashboard.html')

def Login_Page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Fetch the user from the User table
            user = User.objects.get(email=email)

            # Check if the password matches
            if user.password == password:
                # Set the user session here, if necessary
                request.session['user_id'] = user.id  # Store user ID in session
                request.session['usertype'] = user.usertype  # Store usertype in session

                # Redirect based on usertype
                if user.usertype == 1:
                    return redirect('Admin_Dashboard')
                elif user.usertype == 2:
                    return redirect('Moderator_Dashboard')
                elif user.usertype == 3:
                    return redirect('Teacher_Dashboard')
            else:
                # Invalid password
                messages.error(request, 'Invalid password. Please try again.')
        except User.DoesNotExist:
            # User not found
            messages.error(request, 'User with this email does not exist.')

    return render(request, 'Authentication/Login.html')

