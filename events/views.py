import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from .models import Event, Participant, Feedback
from .forms import RegistrationForm, FeedbackForm
from .utils import generate_qr_code, generate_certificate_pdf


def index(request):
    events = Event.objects.annotate(count=Count('participants'))
    return render(request, 'events/index.html', {'events': events})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.save()
            # Generate QR code
            try:
                generate_qr_code(participant)
                participant.save()
            except Exception:
                pass
            messages.success(request,
                f"🎉 Registration successful! Welcome, {participant.name}. "
                f"Your Student ID is {participant.student_id}.")
            return redirect('registration_success', pk=participant.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'events/register.html', {'form': form})


def registration_success(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    return render(request, 'events/registration_success.html', {'participant': participant})


def admin_dashboard(request):
    participants = Participant.objects.select_related('event').order_by('-registered_at')

    # Filters
    event_id = request.GET.get('event')
    search = request.GET.get('search', '').strip()
    attendance_filter = request.GET.get('attendance')

    if event_id:
        participants = participants.filter(event_id=event_id)
    if search:
        participants = participants.filter(
            Q(name__icontains=search) | Q(student_id__icontains=search)
        )
    if attendance_filter == '1':
        participants = participants.filter(attendance=True)
    elif attendance_filter == '0':
        participants = participants.filter(attendance=False)

    events = Event.objects.all()
    stats = {
        'total': Participant.objects.count(),
        'present': Participant.objects.filter(attendance=True).count(),
        'feedback': Participant.objects.filter(feedback_submitted=True).count(),
        'eligible': Participant.objects.filter(attendance=True, feedback_submitted=True).count(),
    }
    return render(request, 'events/admin_dashboard.html', {
        'participants': participants,
        'events': events,
        'stats': stats,
        'selected_event': event_id,
        'search': search,
    })


@require_POST
def toggle_attendance(request, pk):
    """AJAX endpoint to toggle attendance."""
    participant = get_object_or_404(Participant, pk=pk)
    participant.attendance = not participant.attendance
    participant.save()
    return JsonResponse({
        'status': 'ok',
        'attendance': participant.attendance,
        'eligible': participant.eligible_for_certificate,
        'pk': pk,
    })


def feedback(request, pk):
    participant = get_object_or_404(Participant, pk=pk)

    if hasattr(participant, 'feedback'):
        messages.info(request, "You have already submitted feedback for this event.")
        return redirect('admin_dashboard')

    if not participant.attendance:
        messages.warning(request, "Feedback is only available for participants who attended the event.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.participant = participant
            fb.save()
            participant.feedback_submitted = True
            participant.save()
            messages.success(request, "✅ Thank you for your feedback! Your certificate is now available.")
            return redirect('certificate', hash=participant.certificate_hash)
    else:
        form = FeedbackForm()

    return render(request, 'events/feedback.html', {'form': form, 'participant': participant})


def certificate(request, hash):
    participant = get_object_or_404(Participant, certificate_hash=hash)

    # Gatekeeper Logic (CO4)
    if not participant.eligible_for_certificate:
        missing = []
        if not participant.attendance:
            missing.append("attendance must be marked")
        if not participant.feedback_submitted:
            missing.append("feedback must be submitted")
        return render(request, 'events/certificate_denied.html', {
            'participant': participant,
            'missing': missing,
        }, status=403)

    buffer = generate_certificate_pdf(participant)
    response = HttpResponse(buffer, content_type='application/pdf')
    fname = f"certificate_{participant.student_id}_{participant.event.name.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response


def export_csv(request):
    """Export participants as CSV."""
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="participants.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Email', 'Event', 'Registered At',
                     'Attendance', 'Feedback Submitted', 'Certificate Eligible'])
    for p in Participant.objects.select_related('event').order_by('student_id'):
        writer.writerow([
            p.student_id, p.name, p.email, p.event.name,
            p.registered_at.strftime('%Y-%m-%d %H:%M'),
            'Yes' if p.attendance else 'No',
            'Yes' if p.feedback_submitted else 'No',
            'Yes' if p.eligible_for_certificate else 'No',
        ])
    return response
