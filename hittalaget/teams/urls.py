from django.urls import path
from . import views

app_name = "team"

urlpatterns = [
    path("<str:sport>/", views.TeamListView.as_view(), name="list"),
    path("<str:sport>/ny/", views.TeamCreateView.as_view(), name="create"),
    path("<str:sport>/uppdatera/", views.TeamUpdateView.as_view(), name="update"),
    path("<str:sport>/ta-bort/", views.TeamDeleteView.as_view(), name="delete"),
    path("<str:sport>/uppdatera-status/", views.TeamUpdateStatusView.as_view(), name="update_status"),
    path("<str:sport>/<int:team_id>/<str:slug>/", views.TeamDetailView.as_view(), name="detail"),
]