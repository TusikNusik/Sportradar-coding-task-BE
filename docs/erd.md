# Sports Event Calendar ERD

This schema covers the Task 1 database-modeling requirement for the sports calendar.

## Entities

- `Sport`: catalog of supported sports such as football or ice hockey.
- `Venue`: location metadata for an event.
- `Competitor`: team or athlete that can participate in events.
- `Event`: scheduled sports event.
- `EventParticipant`: join table between `Event` and `Competitor`, used to model home/away or generic participants without duplicating event columns.

## Relationships

- One `Sport` has many `Competitor` rows.
- One `Sport` has many `Event` rows.
- One `Venue` hosts many `Event` rows.
- One `Event` has many `EventParticipant` rows.
- One `Competitor` has many `EventParticipant` rows.

## Design Notes

- The schema is normalized so sport, venue, and competitor data are stored once and referenced by foreign keys.
- `EventParticipant` allows more than two participants, while still supporting classic home vs away fixtures.
- Foreign-key field names use the requested underscore prefix: `_sport`, `_venue`, `_event`, `_competitor`.
