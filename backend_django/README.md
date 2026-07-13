# FAQ Chatbot — Django/DRF Backend (Database + Admin Panel)

This is the production-oriented upgrade of the FAQ chatbot: FAQs now live in
a real database (SQLite by default, swap to PostgreSQL for real deployment)
and are managed through Django's built-in admin panel instead of a JSON
file. The same NLTK + TF-IDF cosine similarity matching engine from the
Flask version is reused underneath.

## What changed vs. the Flask version

| | Flask version (`backend/`) | Django version (`backend_django/`) |
|---|---|---|
| FAQ storage | `faqs.json` file | `FAQ` model in the database |
| Editing FAQs | Edit the JSON file, restart server | Django admin panel, live — no restart |
| API | Plain Flask routes | Django REST Framework (`/api/faqs/`, `/api/chat/`) |
| Auth on writes | None | `IsAdminUser` required for create/update/delete |

The matcher is cached in memory after the first request and automatically
invalidated whenever a FAQ is added, edited, deactivated, or deleted through
the admin panel or the API — so changes apply instantly, no server restart.

## Project structure

```
backend_django/
├── faqbot/                 # Django project settings
│   ├── settings.py
│   └── urls.py
├── chatbot/                # the app
│   ├── models.py           # FAQ model
│   ├── admin.py             # admin panel config + cache invalidation
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # FAQViewSet (CRUD) + ChatAPIView
│   ├── urls.py
│   ├── nlp_matcher.py        # same NLTK + TF-IDF engine, DB-backed
│   └── management/commands/seed_faqs.py
├── seed_data/faqs.json      # initial FAQ data to load into the DB
├── requirements.txt
└── manage.py
```

## Setup

```bash
cd backend_django
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_faqs      # loads seed_data/faqs.json into the DB
python manage.py createsuperuser
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000`. The admin panel is at
`http://127.0.0.1:8000/admin/` — log in with the superuser you just created.

The `frontend/script.js` file already points at
`http://127.0.0.1:8000/api/chat/` for this version.

## Managing FAQs

**Via the admin panel** (`/admin/` → Chatbot → FAQs):
- Add, edit, or delete any FAQ.
- Toggle `is_active` to hide a FAQ from the bot without deleting it (e.g. a
  seasonal offer that ended).
- Every save/delete invalidates the matcher cache automatically.

**Via the API** (for building your own admin UI later, e.g. in React):

```bash
# List all FAQs (public, paginated)
GET /api/faqs/

# Create a FAQ (requires admin/staff auth)
POST /api/faqs/
{ "question": "Do you support cash on delivery?", "answer": "Yes, in most cities.", "category": "Payments" }

# Update a FAQ
PATCH /api/faqs/<id>/
{ "is_active": false }

# Delete a FAQ
DELETE /api/faqs/<id>/
```

**Re-seeding from scratch:**
```bash
python manage.py seed_faqs --clear --file path/to/your_faqs.json
```

## Chat endpoint (unchanged behavior)

```bash
POST /api/chat/
{ "message": "how long does shipping take" }
```

```json
{
  "matched": true,
  "answer": "Standard shipping takes 3-5 business days...",
  "matched_question": "How long does shipping take?",
  "score": 0.636
}
```

## Moving to PostgreSQL for real deployment

Swap the `DATABASES` entry in `faqbot/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "faqbot",
        "USER": "your_user",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

Install the driver: `pip install psycopg2-binary`, then re-run
`python manage.py migrate` and `python manage.py seed_faqs`.

## Locking down CORS for production

`settings.py` currently has `CORS_ALLOW_ALL_ORIGINS = True` for easy local
development. Before deploying, replace it with:

```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-real-frontend-domain.com",
]
```

## Suggested next extensions

- Add a `ChatLog` model that records every user message + whether it matched,
  so you can see which questions people ask that aren't covered yet.
- Add categories/tags filtering to `/api/faqs/` for a nicer admin UI.
- Swap TF-IDF for `sentence-transformers` (SBERT) embeddings for better
  synonym/paraphrase handling.
- Add DRF Token or JWT auth if the admin UI becomes a separate React app.
