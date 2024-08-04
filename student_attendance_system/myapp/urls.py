from django.urls import path
from .views import *
from django.contrib import admin
# from student_management_app import views, HodViews, StaffViews, StudentViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name="reg"),
    path('Login/',signin, name='login'),
    path('login-h/', loginpage, name="login-h"),
    path('logout-h/', logoutUser, name="logout-h"),
    path('add_face/',add_face,name="add_face"),
    path('create_model/',create_model,name='create_model'),
    path('view-attendance/',view_attendance,name='view_attendance'),
    path('Student-Home/',mark_attendance,name='mark_attendance'),
    path('Select-Subject/',select_subject,name='select_subject'),
    #teacher
    path('teacher_register/', teacher_register, name='teacher_register'),
    path('teacher_login/', teacher_login, name='teacher_login'),
    path('teacher_home/', teacher_home, name='teacher_home'),
    path('logout-t/', logoutTeacher, name='logout-t'),
    path('teacher-view-attendance/', teacher_view_attendance, name='teacher_view_attendance'),
    #firstpage
    path('', first_portal, name='first_portal'),



]
