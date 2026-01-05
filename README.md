# Helpdesk Support (Django)

A lightweight helpdesk/ticketing application built with Django. It provides a simple workflow for students to create tickets, managers to assign tickets to support agents, and agents to manage and comment on tickets. Attachments are supported for ticket submissions.

## Features
- Create tickets with subject, description, and multiple file attachments (PDF/images).
- Role-based access: Student, SupportAgent, Manager.
- Manager views to list and assign tickets to agents.
- Agent views to see assigned tickets and update status.
- Ticket comments with internal/public flags.

## Tech Stack
- Python 3.10+
- Django (project layout in this repo)
- SQLite (default, `db.sqlite3` in repo)

## Repository layout (key files)
- `manage.py` – Django management entrypoint
- `helpdesk_support/` – Django project settings and WSGI/ASGI
- `tickets/` – main app with models, views, forms, templates
- `accounts/` – account/role management utilities
- `templates/` – project templates (ticket create, lists, details)

## Quick Start (Development)
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (create or update `requirements.txt` if missing):

```bash
pip install -r requirements.txt
# if requirements.txt is not present, at minimum:
pip install django
```

3. Run migrations and create a superuser:

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

4. Create default groups and permissions (provided management command):

```bash
python3 manage.py setup_roles
```

5. Run the dev server:

```bash
python3 manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Roles and How to Assign Agents
- The project expects three groups: `Student`, `SupportAgent`, and `Manager`. Use the `setup_roles` management command to create them.
- To make a user a support agent:

  - Create or edit the user in Django admin and add them to the `SupportAgent` group;
  - Or use the shell:

```bash
python3 manage.py shell
from django.contrib.auth.models import User, Group
u = User.objects.get(username='agent_username')
g = Group.objects.get(name='SupportAgent')
g.user_set.add(u)
```

Once users exist in the `SupportAgent` group, managers can assign tickets to them via the manager assign page.

## Attachments (important implementation notes)
- The ticket creation view reads uploaded files using `request.FILES.getlist("attachments")`.
- The create template includes a file input named `attachments` (multiple) — ensure your browser sends files under that name.
- Uploaded files are saved to `TicketAttachment.file` using `upload_to='tickets/<ticket_id>/'`.

## Troubleshooting
- Empty agent dropdown on assign page: ensure there are users in the `SupportAgent` group (see Roles section).
- Attachments not included in POST: confirm the ticket creation form includes `enctype="multipart/form-data"` and a file input named `attachments`.
- If upload fails due to type/size, server-side validation allows only PDF and common image types and limits files to 10 MB each.

## Tests
- If tests exist in `tickets/tests.py` and `accounts/tests.py`, run them with:

```bash
python3 manage.py test
```

## Development tips
- Use the Django admin to manage users, roles, and departments quickly.
- If you plan to deploy, switch from SQLite to PostgreSQL (update `DATABASES` in `helpdesk_support/settings.py`) and configure `MEDIA_ROOT` and a proper `MEDIA_URL` or object storage for attachments.

## Contributing
- File issues or PRs with clear descriptions. Include steps to reproduce and sample data when relevant.

## License
This repo does not include a license file. 
