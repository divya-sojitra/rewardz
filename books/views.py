from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from .models import Rental

User = get_user_model()


def is_staff(user):
    """Check if user is staff or the requested user"""
    return user.is_staff or user.is_superuser


@login_required
def student_dashboard(request, user_id=None):
    """
    Student rental dashboard showing all rentals for a user.
    Staff can view any user's dashboard.
    Regular users can only view their own.
    """
    # If no user_id provided, show current user's rentals
    if user_id is None:
        student = request.user
    else:
        # Check permissions
        if not (request.user.is_staff or request.user.is_superuser or request.user.id == user_id):
            return HttpResponseForbidden("You don't have permission to view this dashboard.")
        student = get_object_or_404(User, id=user_id)
    
    # Get all rentals for the student with book details
    rentals = Rental.objects.filter(user=student).select_related('book').order_by('-start_date')
    
    # Calculate totals
    total_rentals = rentals.count()
    total_charged_sum = sum(r.total_charged_cents for r in rentals)
    total_books = rentals.values('book').distinct().count()
    
    context = {
        'student': student,
        'rentals': rentals,
        'total_rentals': total_rentals,
        'total_charged_sum': total_charged_sum / 100,  # Convert to dollars
        'total_books': total_books,
        'is_viewing_own': student.id == request.user.id,
    }
    
    return render(request, 'books/student_dashboard.html', context)


@user_passes_test(is_staff)
def all_students_dashboard(request):
    """
    Staff-only view showing all students and their rental summaries.
    """
    # Get all users with their rental counts and totals
    from django.db.models import Count, Sum
    
    students = User.objects.annotate(
        rental_count=Count('rental'),
        total_charged=Sum('rental__total_charged_cents')
    ).filter(rental_count__gt=0).order_by('-rental_count')
    
    context = {
        'students': students,
    }
    
    return render(request, 'books/all_students_dashboard.html', context)
