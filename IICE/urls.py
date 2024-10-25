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
    path('admin-dashboard/Profile', adminViews.Profile, name='Admin_Profile'),
    path('admin-dashboard/Faculty', adminViews.Faculty, name='Faculty'),
    path('Admin-Faculty/<int:userid>/', adminViews.FacultyView, name='FacultyView'),
    path('Admin-Faculty/Add/', adminViews.AddFaculty, name='AddFaculty'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)