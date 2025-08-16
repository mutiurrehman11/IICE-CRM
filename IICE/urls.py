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
from Teacher import views as teacherViews
from Moderator import views as modViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.Login_Page, name='home'),
    path('logout/', adminViews.Logout, name='logout'),
    path('admin-dashboard/', adminViews.Admin_Dashboard, name='Admin_Dashboard'),
    path('admin-dashboard/Profile/', adminViews.Profile, name='Admin_Profile'),
    path('Moderator-Profile/', modViews.Profile, name='Moderator_Profile'),
    path('Teacher-Profile/', teacherViews.Profile, name='Teacher_Profile'),
    path('admin-dashboard/Faculty/', adminViews.Faculty, name='Faculty'),
    path('Admin-Faculty/<int:userid>/', adminViews.FacultyView, name='FacultyView'),
    path('Admin-Faculty/Add/', adminViews.AddFaculty, name='AddFaculty'),
    path('Admin-Faculty/Delete/<int:userid>/', adminViews.DeleteFaculty, name='DeleteFaculty'),
    path('Admin-Sessions/', adminViews.Sessions, name='Sessions'),
    path('Admin-Sessions/<int:sessionid>/', adminViews.SessionView, name='SessionView'),
    path('Admin-Sessions/Students/<int:sessionid>/', adminViews.SessionStudentView, name='SessionStudentView'),
    path('Admin-Sessions/Add/', adminViews.AddSession, name='AddSession'),
    path('Admin-CompletedSessions/', adminViews.CompletedSessions, name='CompletedSessions'),
    path('Admin-Sessions/Delete/<int:sessionid>/', adminViews.DeleteSession, name='DeleteSession'),
    path('Admin-Students/', adminViews.Students, name='Students'),
    path('Moderator-Students/', modViews.Students, name='mod_Students'),
    path('Admin-ExStudents/', adminViews.ExStudents, name='ExStudents'),
    path('Moderator-ExStudents/', modViews.ExStudents, name='mod_ExStudents'),
    path('Admin-Students/Add/', adminViews.AddStudent, name='AddStudent'),
    path('Admin-Students/Add/<int:id>/', adminViews.AddStudent, name='AddStudent_with_id'),
    path('Moderator-Students/Add/', modViews.AddStudent, name='mod_AddStudent'),
    path('Admin-Students/<int:studentid>/', adminViews.StudentView, name='StudentView'),
    path('Moderator-Students/<int:studentid>/', modViews.StudentView, name='mod_StudentView'),
    path('Admin-Students/<int:studentid>/Session/', adminViews.StudentSession, name='StudentSession'),
    path('Moderator-Students/<int:studentid>/Session/', modViews.StudentSession, name='mod_StudentSession'),
    path('Admin-Students/<int:studentid>/Session/Add/', adminViews.AddStudentSession, name='AddStudentSession'),
    path('Moderator-Students/<int:studentid>/Session/Add/', modViews.AddStudentSession, name='mod_AddStudentSession'),
    path('Admin-Students/StudentSession/View/<int:studentsessionid>', adminViews.StudentSessionView, name='StudentSessionView'),
    path('Moderator-Students/StudentSession/View/<int:studentsessionid>', modViews.StudentSessionView, name='mod_StudentSessionView'),
    path('Admin-Students/StudentSession/Delete/<int:studentsessionid>', adminViews.DeleteStudentSession, name='DeleteStudentSession'),
    path('Moderator-Students/StudentSession/Delete/<int:studentsessionid>', modViews.DeleteStudentSession, name='mod_DeleteStudentSession'),
    path("add_fee_payment/<int:session_id>/", adminViews.add_fee_payment, name="add_fee_payment"),
    path('Admin-Students/Delete/<int:studentid>/', adminViews.DeleteStudent, name='DeleteStudent'),
    path('Moderator-Students/Delete/<int:studentid>/', modViews.DeleteStudent, name='mod_DeleteStudent'),
    path('Admin-Leads/', adminViews.Leads, name='Leads'),
    path('Moderator-Leads/', modViews.Leads, name='mod_Leads'),
    path('Admin-AddLead/', adminViews.AddLead, name='AddLead'),
    path('Moderator-AddLead/', modViews.AddLead, name='mod_AddLead'),
    path('Admin-Leads/<int:leadid>/', adminViews.LeadView, name='LeadView'),
    path('Moderator-Leads/<int:leadid>/', modViews.LeadView, name='mod_LeadView'),
    path('Admin-Leads/Delete/<int:leadid>/', adminViews.DeleteLead, name='DeleteLead'),
    path('Moderator-Leads/Delete/<int:leadid>/', modViews.DeleteLead, name='mod_DeleteLead'),
    path('Admin-Attendance/', adminViews.select_course, name='select_course'),
    path('Teacher-Attendance/', teacherViews.select_course, name='tec_select_course'),
    path('Admin-Attendance/Mark/<int:course_id>/', adminViews.mark_attendance, name='mark_attendance'),
    path('Teacher-Attendance/Mark/<int:course_id>/', teacherViews.mark_attendance, name='tec_mark_attendance'),
    path('Admin-Notification/', adminViews.Notification, name='notification'),
    path('Moderator-Notification/', modViews.Notification, name='mod_notification'),
    path('Admin-Notification/Recheck/', adminViews.MakeNotification, name='Recheck'),
    path('Moderator-Notification/Recheck/', modViews.MakeNotification, name='mod_Recheck'),
    path('Admin-Payments/', adminViews.Payment, name='payment'),
    path('print_attendance_report/<int:course_id>/', adminViews.print_attendance_report, name='print_attendance_report'),
    path('Admin-EmailService/', adminViews.EmailService, name='EmailService'),
    path('notify-late-fee-students/', adminViews.notify_late_fee_students, name='notify_late_fee_students'),
    path('send-fee-reminder/', adminViews.send_fee_reminder, name='send_fee_reminder'),
    path('mark-all-notifications-read/', adminViews.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('Admin-Students/<int:studentid>/mark-installment-paid/', adminViews.mark_installment_paid, name='mark_installment_paid'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)