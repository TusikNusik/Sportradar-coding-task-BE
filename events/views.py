from datetime import datetime, time

from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import get_current_timezone, is_naive, make_aware
from django.views.decorators.http import require_http_methods

from .models import Competitor, Event, EventParticipant, Sport, Venue


def _events_queryset():
    return (
        Event.objects.select_related("_sport", "_venue")
        .prefetch_related(
            Prefetch(
                "event_participants",
                queryset=EventParticipant.objects.select_related("_competitor").order_by(
                    "display_order", "id"
                ),
            )
        )
        .order_by("start_datetime", "title")
    )


def _event_to_template_data(event):
    participants = [
        participant._competitor.name for participant in event.event_participants.all()
    ]
    return {
        "id": event.id,
        "title": event.title,
        "start_datetime": event.start_datetime,
        "status": event.get_status_display(),
        "sport_name": event._sport.name,
        "venue": (
            f"{event._venue.name} ({event._venue.city}, {event._venue.country})"
            if event._venue
            else None
        ),
        "description": event.description,
        "round_label": event.round_label,
        "participants": participants,
    }


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _management_page_context(error_message=None, success_message=None):
    return {
        "sports": Sport.objects.order_by("name"),
        "competitors": [
            {
                "id": competitor.id,
                "name": competitor.name,
                "sport_name": competitor._sport.name,
            }
            for competitor in Competitor.objects.select_related("_sport").order_by("name")
        ],
        "competitor_type_choices": Competitor.CompetitorType.choices,
        "error_message": error_message,
        "success_message": success_message,
    }


def _handle_create_sport(post_data):
    sport_name = post_data.get("sport_name", "").strip()
    if not sport_name:
        return "Sport name is required.", None

    try:
        Sport.objects.create(name=sport_name)
        return None, "Sport created."
    except IntegrityError:
        return "This sport already exists.", None


def _handle_create_venue(post_data):
    venue_name = post_data.get("venue_name", "").strip()
    city = post_data.get("city", "").strip()
    country = post_data.get("country", "").strip()
    address = post_data.get("address", "").strip()
    capacity_raw = post_data.get("capacity", "").strip()
    is_indoor = post_data.get("is_indoor") == "on"

    if not venue_name or not city or not country:
        return "Venue name, city, and country are required.", None

    capacity = int(capacity_raw) if capacity_raw.isdigit() else None
    try:
        Venue.objects.create(
            name=venue_name,
            city=city,
            country=country,
            address=address,
            capacity=capacity,
            is_indoor=is_indoor,
        )
        return None, "Venue created."
    except IntegrityError:
        return "This venue already exists in that city and country.", None


def _handle_create_competitor(post_data):
    competitor_name = post_data.get("competitor_name", "").strip()
    short_name = post_data.get("short_name", "").strip()
    competitor_type = post_data.get(
        "competitor_type", Competitor.CompetitorType.TEAM
    )
    competitor_sport_id = post_data.get("competitor_sport_id", "").strip()

    if not competitor_name or not competitor_sport_id:
        return "Participant/team name and sport are required.", None

    try:
        sport = Sport.objects.get(pk=competitor_sport_id)
    except Sport.DoesNotExist:
        return "Selected sport does not exist.", None

    try:
        Competitor.objects.create(
            name=competitor_name,
            short_name=short_name,
            competitor_type=competitor_type,
            _sport=sport,
        )
        return None, "Participant/team created."
    except IntegrityError:
        return "This participant/team already exists for that sport.", None


def _handle_create_event(post_data):
    title = post_data.get("title", "").strip()
    start_datetime_raw = post_data.get("start_datetime", "").strip()
    sport_id = post_data.get("sport_id", "").strip()
    venue_id = post_data.get("venue_id", "").strip()
    description = post_data.get("description", "").strip()
    round_label = post_data.get("round_label", "").strip()
    status = post_data.get("status", Event.Status.SCHEDULED)
    participant_ids = post_data.getlist("participant_ids")

    if not title or not start_datetime_raw or not sport_id:
        return "Title, date/time, and sport are required.", None

    start_datetime = parse_datetime(start_datetime_raw)
    if start_datetime is None:
        return "Invalid date/time format.", None

    if is_naive(start_datetime):
        start_datetime = make_aware(start_datetime, get_current_timezone())

    try:
        sport = Sport.objects.get(pk=sport_id)
    except Sport.DoesNotExist:
        return "Selected sport does not exist.", None

    venue = None
    if venue_id:
        try:
            venue = Venue.objects.get(pk=venue_id)
        except Venue.DoesNotExist:
            return "Selected venue does not exist.", None

    competitors = list(
        Competitor.objects.filter(pk__in=participant_ids, _sport=sport)
    )
    with transaction.atomic():
        event = Event(
            title=title,
            start_datetime=start_datetime,
            status=status,
            description=description,
            round_label=round_label,
            _sport=sport,
            _venue=venue,
        )
        event.save()

        for index, competitor in enumerate(competitors, start=1):
            participant = EventParticipant(
                _event=event,
                _competitor=competitor,
                role=EventParticipant.Role.PARTICIPANT,
                display_order=index,
            )
            participant.save()

    return None, "Event created."


@require_http_methods(["GET", "POST"])
def events_page(request):
    error_message = None
    success_message = None

    if request.method == "POST":
        error_message, success_message = _handle_create_event(request.POST)

    filters = {
        "sport": request.GET.get("sport", ""),
        "status": request.GET.get("status", ""),
        "date_from": request.GET.get("date_from", ""),
        "date_to": request.GET.get("date_to", ""),
    }

    filter_messages: list[str] = []
    queryset = _events_queryset()

    if filters["sport"]:
        queryset = queryset.filter(_sport_id=filters["sport"])

    if filters["status"]:
        queryset = queryset.filter(status=filters["status"])

    tz = get_current_timezone()

    if filters["date_from"]:
        parsed = _parse_date(filters["date_from"])
        if parsed:
            start_bound = make_aware(datetime.combine(parsed, time.min), tz)
            queryset = queryset.filter(start_datetime__gte=start_bound)
        else:
            filter_messages.append("Invalid start date filter.")

    if filters["date_to"]:
        parsed = _parse_date(filters["date_to"])
        if parsed:
            end_bound = make_aware(datetime.combine(parsed, time.max), tz)
            queryset = queryset.filter(start_datetime__lte=end_bound)
        else:
            filter_messages.append("Invalid end date filter.")

    context = {
        "events": [_event_to_template_data(event) for event in queryset],
        "sports": Sport.objects.order_by("name"),
        "venues": Venue.objects.order_by("country", "city", "name"),
        "competitors": [
            {
                "id": competitor.id,
                "name": competitor.name,
                "sport_name": competitor._sport.name,
            }
            for competitor in Competitor.objects.select_related("_sport").order_by("name")
        ],
        "status_choices": Event.Status.choices,
        "active_filters": filters,
        "filter_messages": filter_messages,
        "error_message": error_message,
        "success_message": success_message,
    }
    return render(request, "events/index.html", context)


@require_http_methods(["GET", "POST"])
def manage_page(request):
    error_message = None
    success_message = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_sport":
            error_message, success_message = _handle_create_sport(request.POST)
        elif action == "create_venue":
            error_message, success_message = _handle_create_venue(request.POST)
        elif action == "create_competitor":
            error_message, success_message = _handle_create_competitor(request.POST)
        else:
            error_message = "Unknown action."

    context = _management_page_context(error_message, success_message)
    return render(request, "events/manage.html", context)


@require_http_methods(["GET"])
def event_detail_page(request, event_id):
    event = get_object_or_404(_events_queryset(), pk=event_id)
    return render(request, "events/detail.html", {"event": _event_to_template_data(event)})
