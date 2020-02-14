from django.urls import path
from . import views

app_name = "ad"

urlpatterns = [
    path('<str:sport>/', views.AdListView.as_view(), name="list"),
    path('<str:sport>/ny/', views.AdCreateView.as_view(), name="create"),
    path('<str:sport>/<int:ad_id>/<str:slug>/', views.AdDetailView.as_view(), name="detail"),
    path('<str:sport>/<int:ad_id>/<str:slug>/ta-bort/', views.AdDeleteView.as_view(), name="delete"),   
]


