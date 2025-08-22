from django.shortcuts import render, redirect
from django.contrib import messages

from .models import User
def Login_Page(request):
    if request.method == 'POST':
        if User.objects.count() == 0:
            User.objects.create(first_name="Huzaifa", last_name="Huzaifa", email="callmehuzaifaimran@gmail.com",
                                password="huzaifa12345", usertype=1)
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
                    return redirect('mod_notification')
                elif user.usertype == 3:
                    return redirect('tec_select_course')
            else:
                # Invalid password
                messages.error(request, 'Invalid password. Please try again.')
        except User.DoesNotExist:
            # User not found
            messages.error(request, 'User with this email does not exist.')

    return render(request, 'Authentication/Login.html')

