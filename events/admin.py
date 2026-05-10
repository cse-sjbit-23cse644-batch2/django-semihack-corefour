from django.contrib import admin
from .models import Event, Participant, Feedback


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'venue']
    search_fields = ['name']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'email', 'event', 'attendance', 'feedback_submitted', 'eligible_for_certificate']
    list_filter = ['attendance', 'feedback_submitted', 'event']
    search_fields = ['student_id', 'name', 'email']
    readonly_fields = ['certificate_hash', 'registered_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['participant', 'rating', 'submitted_at']
    list_filter = ['rating']
