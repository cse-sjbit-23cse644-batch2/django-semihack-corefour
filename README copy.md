# EduEvent — Academic Event Lifecycle & Certification System

A Django web application for managing the complete academic event lifecycle:
**Student Registration → QR/Attendance Tracking → Feedback → Conditional PDF Certificate**

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser (admin panel access)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** — add events via `/admin/` first.

### Default Admin
- URL: `/admin/`
- Username: `admin` / Password: `admin123` *(if using seed script)*

---

## ✅ Feature Checklist

| Feature | Status | Description |
|---------|--------|-------------|
| Event Registration | ✅ | Form with server-side duplicate Student ID check |
| AJAX Attendance Toggle | ✅ | Toggle without page refresh via `fetch()` POST |
| Feedback Form | ✅ | Star rating + comments, validation, one per participant |
| Conditional PDF Certificate | ✅ | Gatekeeper: `attendance=True AND feedback_submitted=True` |
| 403 Certificate Denied | ✅ | Shows specific conditions not met |
| QR Code Generation | ✅ | Auto-generated on registration (python-qrcode) |
| CSV Export | ✅ | Download all participant data |
| Responsive UI | ✅ | Bootstrap 5 mobile-first design |
| Django Admin Panel | ✅ | Full CRUD via `/admin/` |

---

## 🎯 CO–SDG Mapping

| Course Outcome | How Demonstrated | SDG Target |
|----------------|------------------|------------|
| **CO1** — Django MVT Architecture | URL routing for all views: `register/`, `dashboard/`, `certificate/<hash>/` in `urls.py` | SDG 4.3 — Equal access to higher education |
| **CO2** — Models & Validated Forms | `Participant(student_id=CharField(unique=True))` in `models.py`; `RegistrationForm.clean_student_id()` for duplicate check; `FeedbackForm` with rating validation | SDG 4.5 — Eliminate gender and wealth disparities |
| **CO3** — Reusable Templates & Responsive Design | `base.html` with `{% block content %}` inheritance; Bootstrap 5 CDN; mobile-first grid system | SDG 4.A — Inclusive and safe learning environments |
| **CO4** — Conditional PDF via ReportLab | `views.py:certificate()` — `if participant.eligible_for_certificate` else `403`; `generate_certificate_pdf()` in `utils.py` | SDG 16.10 — Transparent and accountable institutions |
| **CO5** — AJAX Without Page Refresh | `toggle_attendance(request, pk)` decorated `@require_POST`; frontend uses `fetch()` API and updates DOM without reload | SDG 9.C — Universal ICT access |

---

## 📝 SDG Justification

> *"Our Event Lifecycle system advances **SDG 4: Quality Education** (Target 4.5) by digitizing academic event management — ensuring equitable access to registration and verified certificates regardless of background. The conditional PDF issuance (CO4) supports **SDG 16** (Target 16.10) by providing transparent, tamper-evident certification through cryptographic hashes. Built with Django MVT (CO1) and AJAX (CO5), the system demonstrates responsive design while promoting inclusive participation in academic activities, with QR-coded certificates supporting **SDG 9.C** for universal ICT access to academic credentials."*

---

## 🏗 Project Structure

```
event_lifecycle/
├── event_lifecycle/
│   ├── settings.py          # Django config, installed apps, DB
│   └── urls.py              # Root URL router
├── events/
│   ├── models.py            # Event, Participant, Feedback models (CO1, CO2)
│   ├── forms.py             # RegistrationForm, FeedbackForm with validation (CO2)
│   ├── views.py             # All views incl. AJAX toggle + PDF endpoint (CO4, CO5)
│   ├── urls.py              # App-level URL patterns (CO1)
│   ├── utils.py             # generate_qr_code(), generate_certificate_pdf()
│   └── admin.py             # Django admin configuration
├── templates/events/
│   ├── base.html            # Reusable template with blocks (CO3)
│   ├── index.html           # Home page with event listing
│   ├── register.html        # Registration form (CO2, CO3)
│   ├── registration_success.html  # Post-registration confirmation + QR
│   ├── admin_dashboard.html # Attendance dashboard with AJAX (CO5)
│   ├── feedback.html        # Star-rating feedback form (CO2)
│   └── certificate_denied.html   # 403 gatekeeper page (CO4)
├── static/js/
│   └── ajax_toggle.js       # AJAX attendance toggle script (CO5)
├── requirements.txt
└── README.md
```

---

## 🔑 Key Implementation Details

### Gatekeeper Logic (CO4)
```python
# views.py — certificate()
def certificate(request, hash):
    participant = get_object_or_404(Participant, certificate_hash=hash)
    if not participant.eligible_for_certificate:  # attendance AND feedback
        return render(request, 'certificate_denied.html', status=403)
    buffer = generate_certificate_pdf(participant)
    return HttpResponse(buffer, content_type='application/pdf')
```

### AJAX Attendance Toggle (CO5)
```python
# views.py
@require_POST
def toggle_attendance(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    participant.attendance = not participant.attendance
    participant.save()
    return JsonResponse({'status': 'ok', 'attendance': participant.attendance})
```

### Duplicate ID Validation (CO2)
```python
# forms.py
def clean_student_id(self):
    sid = self.cleaned_data['student_id'].strip().upper()
    if Participant.objects.filter(student_id=sid).exists():
        raise forms.ValidationError("⚠ This Student ID is already registered.")
    return sid
```

---

## 🧪 Verification Checklist

- [x] App loads at `http://127.0.0.1:8000`
- [x] Register participant → saves to DB
- [x] Duplicate ID → shows validation error
- [x] AJAX toggle → DB updates, UI reflects change without refresh
- [x] Feedback submitted → certificate badge changes to "Ready"
- [x] `/certificate/<hash>/` with conditions met → PDF downloads
- [x] `/certificate/<hash>/` without conditions → 403 page with explanation
- [x] Mobile view works (Bootstrap 5 responsive grid)
- [x] QR code generated on registration
- [x] CSV export downloads all participant data
- [x] README has CO-SDG table + SDG justification

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | ≥4.2 | Web framework (MVT, ORM, forms) |
| reportlab | ≥4.0 | PDF certificate generation |
| qrcode[pil] | ≥7.4 | QR code image generation |
| Pillow | ≥10.0 | Image processing for QR codes |
