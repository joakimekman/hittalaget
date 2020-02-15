from django.conf import settings
from django.contrib.auth.views import (
  LoginView,
  LogoutView,
  PasswordChangeView,
  PasswordResetView,
  PasswordResetDoneView,
  PasswordResetConfirmView,
  PasswordResetCompleteView,
)
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from hittalaget.users.forms import SetPasswordForm2


urlpatterns = [
    path('admin/', admin.site.urls),
    path('om-oss/', TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path('contakt/', TemplateView.as_view(template_name="pages/contact.html"), name="contact"),

    path('spelare/', include('hittalaget.players.urls', namespace='player')),
    path('lag/', include('hittalaget.teams.urls', namespace='team')),
    path('annonser/', include('hittalaget.ads.urls', namespace='ad')),
    path('konversationer/', include('hittalaget.conversations.urls', namespace='conversation')),
    
    path('reset-password/', PasswordResetView.as_view(from_email="test@test.com"), name="password_reset"),
    path('reset-password/email-sent/', PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(form_class=SetPasswordForm2), name="password_reset_confirm"),
    path('reset-password/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('', TemplateView.as_view(template_name="pages/index.html"), name="index"),
    path('', include('hittalaget.users.urls', namespace="user")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
  import debug_toolbar

  urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
  ]

  