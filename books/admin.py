from django.contrib import admin
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django.contrib import messages
from .models import Book, Rental
from .utils import create_rental_for_user, extend_rental

User = get_user_model()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'pages', 'openlibrary_id']
    search_fields = ['title', 'openlibrary_id']
    list_filter = ['pages']
    readonly_fields = ['openlibrary_id']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_link',
        'book_title',
        'start_date',
        'months_rented',
        'monthly_fee_display',
        'total_charged_display',
        'extend_button'
    ]
    list_filter = ['user', 'start_date', 'months_rented']
    search_fields = ['user__username', 'user__email', 'book__title']
    readonly_fields = [
        'start_date',
        'monthly_fee_cents',
        'total_charged_cents',
        'monthly_fee_display',
        'total_charged_display'
    ]
    
    # Custom URLs for actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start-rental/', self.admin_site.admin_view(self.start_rental_view), name='books_rental_start'),
            path('<int:rental_id>/extend/', self.admin_site.admin_view(self.extend_rental_view), name='books_rental_extend'),
            path('students-dashboard/', self.admin_site.admin_view(self.students_dashboard_redirect), name='books_students_dashboard'),
        ]
        return custom_urls + urls
    
    def students_dashboard_redirect(self, request):
        """Redirect to the students dashboard view"""
        from django.shortcuts import redirect
        return redirect('books:all_students')
    
    # Display methods
    def user_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        admin_url = reverse('admin:auth_user_change', args=[obj.user.id])
        dashboard_url = reverse('books:student_dashboard', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a> | <a href="{}" target="_blank">📊 Dashboard</a>',
            admin_url, obj.user.username, dashboard_url
        )
    user_link.short_description = 'Student'
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book'
    
    def monthly_fee_display(self, obj):
        return f"${obj.monthly_fee_cents / 100:.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'
    monthly_fee_display.admin_order_field = 'monthly_fee_cents'
    
    def total_charged_display(self, obj):
        return f"${obj.total_charged_cents / 100:.2f}"
    total_charged_display.short_description = 'Total Charged'
    total_charged_display.admin_order_field = 'total_charged_cents'
    
    def extend_button(self, obj):
        from django.urls import reverse
        url = reverse('admin:books_rental_extend', args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Extend Rental</a>',
            url
        )
    extend_button.short_description = 'Actions'
    
    # Custom views
    def start_rental_view(self, request):
        """View to start a new rental"""
        if request.method == 'POST':
            user_id = request.POST.get('user')
            title = request.POST.get('title')
            manual_pages = request.POST.get('manual_pages')
            
            if not user_id or not title:
                messages.error(request, 'User and title are required.')
            else:
                try:
                    user = User.objects.get(id=user_id)
                    
                    # If manual pages provided, create book directly
                    if manual_pages:
                        try:
                            pages = int(manual_pages)
                            book, created = Book.objects.get_or_create(
                                title=title,
                                defaults={'pages': pages}
                            )
                            monthly_fee_cents = int((pages / 100.0) * 100)
                            rental = Rental.objects.create(
                                user=user,
                                book=book,
                                months_rented=1,
                                monthly_fee_cents=monthly_fee_cents,
                                total_charged_cents=0
                            )
                            messages.success(
                                request,
                                f'Rental created for {user.username} - {title} ({pages} pages, ${monthly_fee_cents/100:.2f}/month, first month free)'
                            )
                        except ValueError:
                            messages.error(request, 'Invalid page number.')
                            return render(request, 'admin/books/start_rental.html', {
                                'users': User.objects.all(),
                                'title': 'Start New Rental'
                            })
                    else:
                        # Use OpenLibrary lookup
                        rental = create_rental_for_user(user, title)
                        if rental.book.pages:
                            messages.success(
                                request,
                                f'Rental created for {user.username} - {title} ({rental.book.pages} pages, ${rental.monthly_fee_cents/100:.2f}/month, first month free)'
                            )
                        else:
                            messages.warning(
                                request,
                                f'Rental created for {user.username} - {title} (pages unknown, no monthly fee)'
                            )
                    
                    return redirect('admin:books_rental_changelist')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
                except Exception as e:
                    messages.error(request, f'Error creating rental: {str(e)}')
        
        context = {
            'users': User.objects.all().order_by('username'),
            'title': 'Start New Rental',
            'site_title': 'Django Admin',
            'site_header': 'Administration',
            'has_permission': True,
        }
        return render(request, 'admin/books/start_rental.html', context)
    
    def extend_rental_view(self, request, rental_id):
        """View to extend an existing rental"""
        try:
            rental = Rental.objects.get(id=rental_id)
        except Rental.DoesNotExist:
            messages.error(request, 'Rental not found.')
            return redirect('admin:books_rental_changelist')
        
        if request.method == 'POST':
            try:
                add_months = int(request.POST.get('add_months', 1))
                if add_months < 1:
                    messages.error(request, 'Must add at least 1 month.')
                else:
                    charge = extend_rental(rental, add_months)
                    messages.success(
                        request,
                        f'Rental extended by {add_months} month(s). '
                        f'Charged ${charge/100:.2f}. '
                        f'Total: {rental.months_rented} months, ${rental.total_charged_cents/100:.2f} total charged.'
                    )
                    return redirect('admin:books_rental_changelist')
            except ValueError:
                messages.error(request, 'Invalid number of months.')
            except Exception as e:
                messages.error(request, f'Error extending rental: {str(e)}')
        
        context = {
            'rental': rental,
            'title': f'Extend Rental - {rental.book.title}',
            'site_title': 'Django Admin',
            'site_header': 'Administration',
            'has_permission': True,
        }
        return render(request, 'admin/books/extend_rental.html', context)
    
    # Add link to start rental in changelist
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['start_rental_url'] = 'start-rental/'
        return super().changelist_view(request, extra_context=extra_context)
