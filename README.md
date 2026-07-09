# Photo Classification Platform for Worknomads Inc.

A Django-based platform where users upload photos and the system automatically classifies them as safe or unsafe using two background microservices.

---

## What's inside

```
Photo_Classification_Platform/
├── config/               # Django settings, URLs, WSGI
├── photos/               # Main app — models, views, templates
├── microservices/
│   ├── safe_rule_service/    # Marks processed submissions as safe
│   ├── unsafe_rule_service/  # Marks failed submissions as unsafe
│   └── docker-compose.yml
├── media/                # Uploaded photos land here
├── db.sqlite3            # Local database
├── manage.py
└── requirements.txt
```

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/loye22/Photo_Classification_Platform.git
cd Photo_Classification_Platform
```

### 2. Set up a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create an admin account

```bash
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver
```

The app will be at `http://127.0.0.1:8000`  
Admin panel at `http://127.0.0.1:8000/admin`

---

## Running the microservices

The two classification services run as Docker containers and share the same SQLite database.

Make sure Docker is running, then from the project root:

```bash
cd microservices
docker compose up --build
```

- **safe-rule-service** — checks for submissions with `status = processed` and sets `safety_rule = safe`
- **unsafe-rule-service** — checks for submissions with `status = failed` and sets `safety_rule = unsafe`

---

## Notes

- Photos must be image files only (jpg, png, etc.) and under 4MB
- The microservices connect directly to `db.sqlite3` via a mounted Docker volume
- If you switch to PostgreSQL later, update `DB_PATH` in `docker-compose.yml` and `settings.py` accordingly
