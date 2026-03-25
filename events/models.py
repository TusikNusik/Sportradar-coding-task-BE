from django.db import models
from django.utils.text import slugify


class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_indoor = models.BooleanField(default=False)

    class Meta:
        ordering = ["country", "city", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "city", "country"],
                name="unique_venue_per_city_country",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"


class Competitor(models.Model):
    class CompetitorType(models.TextChoices):
        TEAM = "team", "Team"
        ATHLETE = "athlete", "Athlete"

    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=50, blank=True)
    competitor_type = models.CharField(
        max_length=20,
        choices=CompetitorType.choices,
        default=CompetitorType.TEAM,
    )
    _sport = models.ForeignKey(
        Sport,
        on_delete=models.PROTECT,
        related_name="competitors",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "_sport"],
                name="unique_competitor_per_sport",
            )
        ]

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        POSTPONED = "postponed", "Postponed"
        CANCELLED = "cancelled", "Cancelled"
        FINISHED = "finished", "Finished"

    title = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    description = models.TextField(blank=True)
    round_label = models.CharField(max_length=100, blank=True)
    _sport = models.ForeignKey(
        Sport,
        on_delete=models.PROTECT,
        related_name="events",
    )
    _venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    class Meta:
        ordering = ["start_datetime", "title"]

    def __str__(self):
        return f"{self.title} @ {self.start_datetime:%Y-%m-%d %H:%M}"


class EventParticipant(models.Model):
    class Role(models.TextChoices):
        HOME = "home", "Home"
        AWAY = "away", "Away"
        PARTICIPANT = "participant", "Participant"

    _event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_participants",
    )
    _competitor = models.ForeignKey(
        Competitor,
        on_delete=models.PROTECT,
        related_name="event_participations",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT,
    )
    display_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["_event", "display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["_event", "_competitor"],
                name="unique_competitor_per_event",
            )
        ]

    def __str__(self):
        return f"{self._event.title}: {self._competitor.name}"
