from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Student dashboard - view own rentals
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # Student dashboard - view specific student (staff only)
    path('dashboard/<int:user_id>/', views.student_dashboard, name='student_dashboard'),
    
    # All students overview (staff only)
    path('students/', views.all_students_dashboard, name='all_students'),
]
