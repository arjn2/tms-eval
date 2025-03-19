from django.urls import path
from .views import handle_admin_requests, send_request_note

urlpatterns = [
    # Admin Travel Request Handling
    path('travel-request/', handle_admin_requests, name='admin_travel_requests'),  # List or Create Travel Requests
    path('travel-request/<int:id>/', handle_admin_requests, name='admin_travel_request_detail'),  # Specific Request by ID
    
    # Sending Notes Based on Travel Request ID
    path('travel-request/<int:id>/note/', send_request_note, name='admin_travel_request_note'),
]
