from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "user"

urlpatterns = [
  path('skapa-konto/', views.UserCreateView.as_view(), name="register"),
  path('logga-in/', views.UserLoginView.as_view(), name="login"),
  path('logga-ut/', LogoutView.as_view(), name="logout"),
  path('~redirect/', views.UserRedirectView.as_view(), name="redirect"),

  path('installningar/', views.UserUpdateView.as_view(), name="update_account"),
  path('avregistrera-konto/', views.UserDeleteView.as_view(), name="delete_account"),
  path('nytt-losenord/', views.UserPasswordChangeView.as_view(), name="password_change"),

  path('<username>/', views.UserDetailView.as_view(), name="detail"),
]


