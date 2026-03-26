from django.test import TestCase
from django.urls import reverse

from .models import Competitor, Event, EventParticipant, Sport, Venue


class EventsPageTests(TestCase):
    def setUp(self):
        self.sport = Sport.objects.create(name="Football")
        self.second_sport = Sport.objects.create(name="Ice Hockey")
        self.venue = Venue.objects.create(
            name="National Stadium",
            city="Warsaw",
            country="Poland",
        )
        self.home = Competitor.objects.create(name="Salzburg", _sport=self.sport)
        self.away = Competitor.objects.create(name="Sturm", _sport=self.sport)

    def _create_event(self, title, sport):
        event = Event(
            title=title,
            start_datetime="2026-07-18T18:30:00Z",
            _sport=sport,
            _venue=self.venue,
        )
        event.save()
        EventParticipant(
            _event=event,
            _competitor=self.home,
            role=EventParticipant.Role.HOME,
            display_order=1,
        ).save()
        return event

    def test_events_page_renders(self):
        self._create_event("Salzburg vs Sturm", self.sport)

        response = self.client.get(reverse("events-page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Salzburg vs Sturm")
        self.assertContains(response, "National Stadium")
        self.assertContains(response, "Salzburg")

    def test_filters_by_sport(self):
        self._create_event("Football Match", self.sport)
        self._create_event("Hockey Match", self.second_sport)

        response = self.client.get(reverse("events-page"), {"sport": self.second_sport.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hockey Match")
        self.assertNotContains(response, "Football Match")

    def test_post_creates_event_and_participants(self):
        payload = {
            "title": "Salzburg vs Sturm",
            "start_datetime": "2026-07-18T18:30",
            "sport_id": str(self.sport.id),
            "venue_id": str(self.venue.id),
            "status": Event.Status.SCHEDULED,
            "participant_ids": [str(self.home.id), str(self.away.id)],
        }

        response = self.client.post(reverse("events-page"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(EventParticipant.objects.count(), 2)

        created = Event.objects.get()
        self.assertEqual(created.title, "Salzburg vs Sturm")
        self.assertEqual(created._sport_id, self.sport.id)


class ManagePageTests(TestCase):
    def setUp(self):
        self.sport = Sport.objects.create(name="Football")

    def test_post_creates_sport(self):
        response = self.client.post(
            reverse("events-manage-page"),
            {"action": "create_sport", "sport_name": "Basketball"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Sport.objects.filter(name="Basketball").exists())

    def test_post_creates_competitor(self):
        payload = {
            "action": "create_competitor",
            "competitor_name": "Capitals",
            "short_name": "CAP",
            "competitor_sport_id": str(self.sport.id),
        }

        response = self.client.post(reverse("events-manage-page"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Competitor.objects.filter(name="Capitals").exists())
