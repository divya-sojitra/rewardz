#!/usr/bin/env python
"""
Setup script to create test data for the rental system
Run: python setup_test_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_site.settings')
django.setup()

from django.contrib.auth import get_user_model
from books.models import Book, Rental

User = get_user_model()

def create_test_data():
    print("🚀 Setting up test data...\n")
    
    # Create test users (students)
    students = [
        ('alice', 'alice@example.com', 'Alice', 'Smith'),
        ('bob', 'bob@example.com', 'Bob', 'Johnson'),
        ('charlie', 'charlie@example.com', 'Charlie', 'Williams'),
    ]
    
    created_users = []
    for username, email, first_name, last_name in students:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ Created student: {username}")
        else:
            print(f"ℹ️  Student already exists: {username}")
        created_users.append(user)
    
    # Create test books with known page counts
    books_data = [
        ('The Great Gatsby', 180),
        ('To Kill a Mockingbird', 281),
        ('1984', 328),
        ('Pride and Prejudice', 432),
        ('The Hobbit', 310),
    ]
    
    created_books = []
    for title, pages in books_data:
        book, created = Book.objects.get_or_create(
            title=title,
            defaults={'pages': pages}
        )
        if created:
            print(f"✅ Created book: {title} ({pages} pages)")
        else:
            print(f"ℹ️  Book already exists: {title}")
        created_books.append(book)
    
    # Create some sample rentals
    print("\n📚 Creating sample rentals...")
    
    if created_users and created_books:
        # Alice rents The Great Gatsby
        rental1, created = Rental.objects.get_or_create(
            user=created_users[0],
            book=created_books[0],
            defaults={
                'months_rented': 1,
                'monthly_fee_cents': 180,  # $1.80/month
                'total_charged_cents': 0
            }
        )
        if created:
            print(f"✅ {created_users[0].username} rented '{created_books[0].title}'")
        
        # Bob rents 1984 (extended to 3 months)
        rental2, created = Rental.objects.get_or_create(
            user=created_users[1],
            book=created_books[2],
            defaults={
                'months_rented': 3,
                'monthly_fee_cents': 328,  # $3.28/month
                'total_charged_cents': 656  # 2 months charged (first free)
            }
        )
        if created:
            print(f"✅ {created_users[1].username} rented '{created_books[2].title}' (3 months)")
    
    print("\n✨ Test data setup complete!")
    print("\n📊 Summary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Books: {Book.objects.count()}")
    print(f"   Rentals: {Rental.objects.count()}")
    print("\n🔗 Access admin at: http://127.0.0.1:8000/admin/")
    print("   Use your superuser credentials to login\n")

if __name__ == "__main__":
    create_test_data()
