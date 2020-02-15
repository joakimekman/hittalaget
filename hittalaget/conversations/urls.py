from django.urls import path
from . import views

app_name = "conversation"

urlpatterns = [
    # PM conversations
    path('pm/<str:username>/', views.ConversationDetailView.as_view(), name="detail"),
    path('pm/<str:username>/nytt-meddelande/', views.ConversationCreateView.as_view(), name="create"),
    path('pm/<str:username>/ta-bort/', views.ConversationDeleteView.as_view(), name="delete"),
    
    # AD conversations
    path('ad/<int:conversation_id>/', views.AdConversationDetailView.as_view(), name="detail_ad"),
    path('ad/<int:conversation_id>/nytt-meddelande/', views.AdConversationMessageView.as_view(), name="message_ad"),
    path('ad/<int:ad_id>/kontakta/', views.AdConversationCreateView.as_view(), name="create_ad"),
    path('ad/<int:conversation_id>/ta-bort/', views.AdConversationDeleteView.as_view(), name="delete_ad"),
    
    path('<str:label>/', views.ConversationListView.as_view(), name="list"),
]

