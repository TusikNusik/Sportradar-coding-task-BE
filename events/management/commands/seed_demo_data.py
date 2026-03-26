from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from events.models import Competitor, Event, EventParticipant, Sport, Venue


class Command(BaseCommand):
    help = "Seed demo sports calendar data (sports, venues, participants, events)."

    @transaction.atomic
    def handle(self, *args, **options):
        football, _ = Sport.objects.get_or_create(name="Football")
        ice_hockey, _ = Sport.objects.get_or_create(name="Ice Hockey")

        stadion, _ = Venue.objects.get_or_create(
            name="Red Bull Arena",
            city="Salzburg",
            country="Austria",
            defaults={"is_indoor": False, "capacity": 30188},
        )
        arena, _ = Venue.objects.get_or_create(
            name="Klagenfurt Arena",
            city="Klagenfurt",
            country="Austria",
            defaults={"is_indoor": True, "capacity": 5000},
        )

        salzburg, _ = Competitor.objects.get_or_create(
            name="Salzburg",
            _sport=football,
            defaults={"short_name": "RBS", "competitor_type": Competitor.CompetitorType.TEAM},
        )
        sturm, _ = Competitor.objects.get_or_create(
            name="Sturm",
            _sport=football,
            defaults={"short_name": "STU", "competitor_type": Competitor.CompetitorType.TEAM},
        )
        kac, _ = Competitor.objects.get_or_create(
            name="KAC",
            _sport=ice_hockey,
            defaults={"short_name": "KAC", "competitor_type": Competitor.CompetitorType.TEAM},
        )
        capitals, _ = Competitor.objects.get_or_create(
            name="Capitals",
            _sport=ice_hockey,
            defaults={"short_name": "CAP", "competitor_type": Competitor.CompetitorType.TEAM},
        )

        football_event, _ = Event.objects.get_or_create(
            title="Salzburg vs Sturm",
            start_datetime=timezone.datetime(2026, 7, 18, 18, 30, tzinfo=timezone.UTC),
            _sport=football,
            defaults={"_venue": stadion, "status": Event.Status.SCHEDULED},
        )
        hockey_event, _ = Event.objects.get_or_create(
            title="KAC vs Capitals",
            start_datetime=timezone.datetime(2026, 10, 23, 9, 45, tzinfo=timezone.UTC),
            _sport=ice_hockey,
            defaults={"_venue": arena, "status": Event.Status.SCHEDULED},
        )

        EventParticipant.objects.get_or_create(
            _event=football_event,
            _competitor=salzburg,
            defaults={"role": EventParticipant.Role.HOME, "display_order": 1},
        )
        EventParticipant.objects.get_or_create(
            _event=football_event,
            _competitor=sturm,
            defaults={"role": EventParticipant.Role.AWAY, "display_order": 2},
        )
        EventParticipant.objects.get_or_create(
            _event=hockey_event,
            _competitor=kac,
            defaults={"role": EventParticipant.Role.HOME, "display_order": 1},
        )
        EventParticipant.objects.get_or_create(
            _event=hockey_event,
            _competitor=capitals,
            defaults={"role": EventParticipant.Role.AWAY, "display_order": 2},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
