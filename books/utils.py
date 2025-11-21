import requests
import urllib.parse


def fetch_pages_for_title(title):
    """
    Fetch the number of pages for a book title from OpenLibrary API.
    
    Args:
        title (str): The book title to search for
        
    Returns:
        tuple: (pages, openlibrary_id) where pages is int or None, 
               and openlibrary_id is str or None
    """
    q = urllib.parse.quote(title)
    url = f"https://openlibrary.org/search.json?title={q}"
    
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        docs = data.get("docs", [])
        
        if not docs:
            return None, None
        
        doc = docs[0]
        pages = doc.get("number_of_pages") or doc.get("number_of_pages_median")
        openlibrary_id = doc.get("key")  # e.g., "/works/OL45883W"
        
        return pages, openlibrary_id
    
    except (requests.RequestException, ValueError) as e:
        # Log error in production, for now return None
        print(f"Error fetching OpenLibrary data: {e}")
        return None, None


def create_rental_for_user(user, title):
    """
    Create a rental for a user by looking up book info from OpenLibrary.
    
    Args:
        user: Django User instance
        title (str): Book title to search for
        
    Returns:
        Rental: The created rental instance
    """
    from .models import Book, Rental
    
    # Fetch book info from OpenLibrary
    pages, openlibrary_id = fetch_pages_for_title(title)
    
    # Create or update Book record
    book, created = Book.objects.get_or_create(
        title=title,
        defaults={
            'pages': pages,
            'openlibrary_id': openlibrary_id
        }
    )
    
    # If book already exists but we got new data, update it
    if not created and (pages or openlibrary_id):
        if pages and not book.pages:
            book.pages = pages
        if openlibrary_id and not book.openlibrary_id:
            book.openlibrary_id = openlibrary_id
        book.save()
    
    # Calculate monthly fee from pages
    monthly_fee_cents = 0
    if book.pages:
        monthly_fee_cents = int((book.pages / 100.0) * 100)
    
    # Create Rental with months_rented=1 (first month is free)
    rental = Rental.objects.create(
        user=user,
        book=book,
        months_rented=1,
        monthly_fee_cents=monthly_fee_cents,
        total_charged_cents=0  # First month is free
    )
    
    return rental


def extend_rental(rental, add_months=1):
    """
    Extend a rental by N months and apply charges.
    
    First month is free. After that, charge (pages/100) dollars per month.
    
    Args:
        rental: Rental instance to extend
        add_months (int): Number of months to add (default 1)
        
    Returns:
        int: Amount charged in cents for this extension
    """
    # Get monthly fee from pages
    monthly = rental.compute_monthly_fee_from_pages()
    
    # Track previous state
    prev_months = rental.months_rented
    
    # Update months rented
    rental.months_rented += add_months
    
    # Calculate how many months to charge
    # First month is free, so we only charge for months beyond the first
    prev_chargeable = max(0, prev_months - 1)
    new_chargeable = max(0, rental.months_rented - 1)
    months_to_charge_now = new_chargeable - prev_chargeable
    
    # Calculate charge amount
    charge = monthly * months_to_charge_now
    
    # Update rental record
    rental.total_charged_cents += charge
    rental.monthly_fee_cents = monthly
    rental.save()
    
    return charge
