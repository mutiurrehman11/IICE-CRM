from django.shortcuts import render, redirect
from django.contrib import messages

from .models import User

def Moderator_Dashboard(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object

    context = {
        'user': user,  # Pass the user object to the template
    }
    return render(request, 'Admin/Dashboard.html',context)
def Teacher_Dashboard(request):
    if 'user_id' not in request.session:
        return redirect('home')
    user_id = request.session.get('user_id')  # Get the logged-in user ID from the session
    user = User.objects.get(id=user_id)  # Fetch the user object

    context = {
        'user': user,  # Pass the user object to the template
    }
    return render(request, 'Admin/Dashboard.html',context)

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

