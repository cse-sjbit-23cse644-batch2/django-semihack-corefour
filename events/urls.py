from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('register/success/<int:pk>/', views.registration_success, name='registration_success'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/toggle/<int:pk>/', views.toggle_attendance, name='toggle_attendance'),
    path('feedback/<int:pk>/', views.feedback, name='feedback'),
    path('certificate/<str:hash>/', views.certificate, name='certificate'),
    path('export/csv/', views.export_csv, name='export_csv'),
]
