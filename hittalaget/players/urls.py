from django.urls import path
from . import views

app_name = "player"

urlpatterns = [
    path('<str:sport>/', views.PlayerListView.as_view(), name="list"),
    path('<str:sport>/ny/', views.PlayerCreateView.as_view(), name="create"),
    path('<str:sport>/uppdatera/', views.PlayerUpdateView.as_view(), name="update"),
    path('<str:sport>/ta-bort/', views.PlayerDeleteView.as_view(), name="delete"),
    path('<str:sport>/uppdatera-status/', views.PlayerUpdateStatusView.as_view(), name="update_status"),
    path('<str:sport>/historik/ny/', views.HistoryCreateView.as_view(), name="create_history"),
    path('<str:sport>/historik/<int:id>/ta-bort/', views.HistoryDeleteView.as_view(), name="delete_history"),
    path('<str:sport>/<str:username>/', views.PlayerDetailView.as_view(), name="detail"),
]


