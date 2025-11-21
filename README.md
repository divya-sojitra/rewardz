# Book Rental Management System

A Django-based web application for managing student book rentals with automatic fee calculation based on OpenLibrary data.

## Features

- 📚 **Automatic Book Lookup**: Fetches book details (pages, OpenLibrary ID) from OpenLibrary API
- 💰 **Smart Fee Calculation**: Monthly fee = (pages / 100) dollars
- 🎁 **First Month Free**: No charge for the first month of rental
- 🔄 **Easy Extension**: Extend rentals with automatic charge calculation
- 👨‍💼 **Admin Interface**: Powerful Django admin with custom actions

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/admin/

## Using the Admin Interface

### Starting a New Rental

1. Log in to Django admin
2. Go to **Rentals** section
3. Click **"Start New Rental"** button
4. Fill in:
   - **Student**: Select from dropdown
   - **Book Title**: Enter title (e.g., "The Great Gatsby")
   - **Pages** (optional): Manual override if OpenLibrary lookup fails
5. Click **"Create Rental"**

The system will:
- Query OpenLibrary API for book details
- Create or update Book record
- Create Rental with first month FREE
- Calculate monthly fee: (pages / 100) dollars

### Extending a Rental

1. Go to **Rentals** list
2. Click **"Extend Rental"** button for any rental
3. Enter number of months to add (default: 1)
4. See live preview of charges
5. Click **"Extend Rental"**

**Charging Logic:**
- First month: FREE
- Additional months: Charged at (pages/100) dollars per month
- Only NEW months are charged (no double-charging)

### Viewing Rental Details

The Rentals list shows:
- Student name (clickable link)
- Book title
- Start date
- Total months rented
- Monthly fee (in dollars)
- Total amount charged (in dollars)
- Quick "Extend" action button

**Filters Available:**
- By student
- By start date
- By months rented

**Search:** Search by student username, email, or book title

## Models

### Book
- `title`: Book title (CharField, max 500)
- `openlibrary_id`: OpenLibrary identifier (CharField, optional)
- `pages`: Number of pages (PositiveIntegerField, nullable)

### Rental
- `user`: Student (ForeignKey to User)
- `book`: Book being rented (ForeignKey to Book)
- `start_date`: When rental started (auto-set)
- `months_rented`: Total months (default: 1)
- `monthly_fee_cents`: Fee per month in cents
- `total_charged_cents`: Cumulative charges in cents

## OpenLibrary Integration

### API Endpoint
```
https://openlibrary.org/search.json?title=YOUR_TITLE
```

### Fields Used
- `number_of_pages` or `number_of_pages_median`
- `key` (OpenLibrary work ID)

### Fallback Behavior
If OpenLibrary:
- Returns no results: Book created with `pages=None`, fee=$0.00/month
- Times out: Same fallback
- Manual override: Admin can specify pages directly

## Fee Calculation Examples

| Pages | Monthly Fee | 1st Month | 2nd Month | 3rd Month | Total (3 months) |
|-------|-------------|-----------|-----------|-----------|------------------|
| 100   | $1.00       | $0.00     | $1.00     | $1.00     | $2.00            |
| 300   | $3.00       | $0.00     | $3.00     | $3.00     | $6.00            |
| 500   | $5.00       | $0.00     | $5.00     | $5.00     | $10.00           |

## Testing

### Using Django Shell

```bash
python manage.py shell
```

```python
# Create test user
from django.contrib.auth.models import User
user = User.objects.create_user('student1', 'student1@test.com', 'pass123')

# Create rental with manual book
from books.models import Book, Rental
book = Book.objects.create(title="Test Book", pages=300)
rental = Rental.objects.create(user=user, book=book, months_rented=1, monthly_fee_cents=300)

# Test extension
from books.utils import extend_rental
charge = extend_rental(rental, add_months=2)
print(f"Charged: ${charge/100:.2f}")
print(f"Total months: {rental.months_rented}")
print(f"Total charged: ${rental.total_charged_cents/100:.2f}")
```

### Testing OpenLibrary Integration

```python
from books.utils import fetch_pages_for_title, create_rental_for_user

# Test API
pages, ol_id = fetch_pages_for_title("The Hobbit")
print(f"Pages: {pages}, ID: {ol_id}")

# Create rental with API lookup
rental = create_rental_for_user(user, "Harry Potter and the Sorcerer's Stone")
print(f"Created: {rental.book.title}, {rental.book.pages} pages")
```

## Project Structure

```
rental_site/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── rental_site/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── books/
    ├── models.py          # Book, Rental models
    ├── admin.py           # Admin interface customizations
    ├── utils.py           # OpenLibrary integration, fee logic
    ├── templates/
    │   └── admin/
    │       └── books/
    │           ├── start_rental.html
    │           ├── extend_rental.html
    │           └── rental/
    │               └── change_list.html
    └── migrations/
```

## Technical Notes

### Money Handling
- All fees stored in **cents** (integers) to avoid floating-point errors
- Display values converted to dollars ($X.XX)
- Formula: `(pages / 100) dollars * 100 = pages cents per month`

### First Month Free Implementation
- `months_rented` starts at 1
- `total_charged_cents` starts at 0
- Extension charges only for months beyond the first:
  ```python
  chargeable_months = max(0, total_months - 1)
  ```

### Idempotency
- Tracks `total_charged_cents` to prevent double-charging
- Extension only charges for NEW months added

## Dependencies

- Django 5.2.8
- djangorestframework (for future API endpoints)
- requests (for OpenLibrary integration)

## Future Enhancements

- [ ] REST API endpoints for rentals
- [ ] Student dashboard (view own rentals)
- [ ] Transaction/Payment history model
- [ ] Email notifications on rental extension
- [ ] Book recommendations based on rental history
- [ ] Bulk operations (extend multiple rentals)
- [ ] Export rental reports (CSV/PDF)

## License

MIT

## Author

Created for book rental management system.
