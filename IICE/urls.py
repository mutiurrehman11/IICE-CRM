"""
URL configuration for IICE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

# App Paths
from authentication import views
from Admin import views as adminViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.Login_Page, name='home'),
    path('logout/', adminViews.Logout, name='logout'),
    path('admin-dashboard/', adminViews.Admin_Dashboard, name='Admin_Dashboard'),
    path('moderator-dashboard/', views.Moderator_Dashboard, name='Moderator_Dashboard'),
    path('teacher-dashboard/', views.Teacher_Dashboard, name='Teacher_Dashboard'),
    path('admin-dashboard/Profile/', adminViews.Profile, name='Admin_Profile'),
    path('admin-dashboard/Faculty/', adminViews.Faculty, name='Faculty'),
    path('Admin-Faculty/<int:userid>/', adminViews.FacultyView, name='FacultyView'),
    path('Admin-Faculty/Add/', adminViews.AddFaculty, name='AddFaculty'),
    path('Admin-Faculty/Delete/<int:userid>/', adminViews.DeleteFaculty, name='DeleteFaculty'),
    path('Admin-Sessions/', adminViews.Sessions, name='Sessions'),
    path('Admin-Sessions/<int:sessionid>/', adminViews.SessionView, name='SessionView'),
    path('Admin-Sessions/Add/', adminViews.AddSession, name='AddSession'),
    path('Admin-CompletedSessions/', adminViews.CompletedSessions, name='CompletedSessions'),
    path('Admin-Sessions/Delete/<int:sessionid>/', adminViews.DeleteSession, name='DeleteSession'),
    path('Admin-Students/', adminViews.Students, name='Students'),
    path('Admin-ExStudents/', adminViews.ExStudents, name='ExStudents'),
    path('Admin-Students/Add/', adminViews.AddStudent, name='AddStudent'),
    path('Admin-Students/<int:studentid>/', adminViews.StudentView, name='StudentView'),
    path('Admin-Students/<int:studentid>/Session/', adminViews.StudentSession, name='StudentSession'),
    path('Admin-Students/Delete/<int:studentid>/', adminViews.DeleteStudent, name='DeleteStudent'),
    path('Admin-Leads/', adminViews.Leads, name='Leads'),
    path('Admin-Leads/Add/', adminViews.AddLead, name='AddLead'),
    path('Admin-Leads/<int:leadid>/', adminViews.LeadView, name='LeadView'),
    path('Admin-Leads/Delete/<int:leadid>/', adminViews.DeleteLead, name='DeleteLead'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)