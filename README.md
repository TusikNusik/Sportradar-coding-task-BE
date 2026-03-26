# Sports Event Calendar

## Solution Overview
I chose **Django** and a classic multi-app project layout because it lets me model the required entities quickly while keeping migrations, views, and templates organized. The domain is represented by five tables—Sport, Venue, Competitor, Event, and EventParticipant—mapped in `events/models.py`, mirroring the ERD in `docs/erd.md`.

The backend exposes three core views: listing/creation (`events_page`), reference-data management (`manage_page`), and event detail (`event_detail_page`). A shared queryset helper applies `select_related`/`prefetch_related` to honor the “no SQL in loops” guidance, and all event creation happens inside a transaction so participant rows stay consistent. To recreate the PDF’s sample fixtures, the `seed_demo_data` management command seeds Salzburg vs. Sturm and KAC vs. Capitals with venues and competitors.

On the frontend, Django templates render a navigation bar with placeholder links, filter controls, the “Add Event” form, and detail pages. Styling relies on a single CSS file under `events/static/` to keep the UI clean without pulling additional frameworks. I verified the critical flows with Django TestCase tests to ensure the brief’s functionality holds up when the app evolves.

## Requirements
- Python 3.11+
- pip
- (Optional) virtual environment tool such as `python -m venv`

Python dependencies are pinned in `requirements.txt` and currently limited to `Django==6.0.3`.

## Project Setup
```bash
git clone https://github.com/TusikNusik/Sportradar-coding-task-BE
cd Sportradar-coding-task-BE
python3 -m venv .venv
source .venv/bin/activate 
python3 -m pip install -r requirements.txt
python manage.py migrate
```

This repository intentionally ships **without** `db.sqlite3`. Running the `migrate` command above (and, optionally, the seed step below) against a clean checkout creates the database file from scratch, so you can safely delete it whenever you want a fresh start.

### Seed Demo Content (Optional)
```bash
python manage.py seed_demo_data
```
This populates the football and ice-hockey examples cited in the assignment (Salzburg vs. Sturm on 18 Jul 2019 and KAC vs. Capitals on 23 Oct 2019, adjusted to timezone-aware datetimes).

## Running the Application
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ and you will find:
- Events list with filters for sport, status, and date range.
- “Add Event” form on the left column.
- Navigation links (Home, Events, Teams, About, Manage) to satisfy the PDF’s navbar requirement.
- Detail pages at `/events/<id>/` for each event.

Visit `/manage/` to add sports, venues, and participants before creating events if you skipped the seed step.

## Running Tests
```bash
python manage.py test
```
Tests cover rendering, filtering, and POST-based creation on the events page, plus sport/competitor creation via the management page.

## Repository Layout
- `callendar/` – Django project configuration, settings, and root URL routing.
- `events/` – Application logic (models, views, templates, static assets, tests, and management command).
- `docs/erd.md` – ERD write-up corresponding to Task 1.
- `manage.py` – Django entry point for dev server, migrations, etc.
- `requirements.txt` – Python dependencies consumed by the virtual environment.
