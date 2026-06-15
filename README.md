# Pizza QA

A lightweight Q&A platform for schools — a simpler alternative to Piazza. Students
post questions inside the subjects they're enrolled in, teachers answer them, and
everyone can join the follow-up discussion.

Built with **Django 5.2**, **Bootstrap 5**, and **SQLite**.

## Features

- **Accounts & roles** — custom user model with `student` and `teacher` roles.
  Students self-register; teacher accounts are created via the Django admin.
- **Subject enrolment** — teachers register the subjects/years they teach;
  students enrol in subjects and pick their teacher (teacher dropdown is filtered
  by subject + year via AJAX).
- **Questions & answers** — post questions (with optional image), mark them
  resolved, optionally make a question visible to teachers only.
- **Follow-up discussion** — threaded follow-up messages under each question, with
  one level of replies.
- **Search & filter** — search a subject's questions by keyword/tag and filter by
  status (all / unresolved / resolved / unanswered).
- **Notifications** — in-app bell with an unread count; you're notified when your
  question is answered or your follow-up gets a reply.
- **Light/dark mode** — toggle in the navbar, remembered per browser.

## Getting started (local development)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database (creates db.sqlite3, seeds subjects and year groups)
python manage.py migrate

# 4. Create an admin / teacher account
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

- Students register at `/users/register/student/`.
- Teachers are created in the admin (`/admin/`) or with `createsuperuser`.
  Set their **role** to `teacher`, then give them subjects to teach via
  "Manage Subjects" in the app.

## Running tests

```bash
python manage.py test
```

## Project layout

- `pizza_qa/` — project settings and root URLs
- `users/` — custom user model, registration, login, student management
- `qa/` — subjects, questions, answers, follow-ups, notifications
- `templates/` — Django templates (server-rendered HTML)
- `media/` — uploaded question/answer images (created at runtime)
