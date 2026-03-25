from django.contrib import admin

from .models import Competitor, Event, EventParticipant, Sport, Venue


admin.site.register(Sport)
admin.site.register(Venue)
admin.site.register(Competitor)
admin.site.register(Event)
admin.site.register(EventParticipant)
