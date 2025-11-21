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
source venv/bin/activate
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
