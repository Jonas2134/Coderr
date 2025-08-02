# Coderr Backend

This is the backend API for **Coderr**, a freelancer marketplace platform connecting customers with business users.
Built with **Django** and **Django REST Framework (DRF)**, it supports role-based registration, offer management, orders, reviews, and more.

---

## Features

- Role-based user registration (`customer` / `business`)
- JWT token-based authentication (login/refresh)
- Profile management per user type
- Offer creation with tiered pricing (`basic`, `standard`, `premium`)
- Order creation and tracking
- Review system with rating/comments
- Statistics endpoint for public insights
- Admin panel support

---

## Requirements

- Python 3.x
- Django **4.x**
- Django REST Framework
- Virtual environment (`venv` or `env`)
- [pip](https://pip.pypa.io/en/stable/)

---

## Installation

1. Clone the repository:
    ```bash
    git clone <REPO-URL>
    cd coderr-backend
    ```
2. Create and activate a virtual environment:
    ```bash
    # Linux/macOS
    python3 -m venv env
    source env/bin/activate
    # Windows
    python -m venv env
    env\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5. (Optional) Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

---

## Start the project

- Start the Django development server with:
    ```bash
    python manage.py runserver
    ```
- The backend is then typically available at: `http://localhost:8000/`
