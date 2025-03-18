from django.urls import path
from .views import handle_manager_requests

urlpatterns = [
    path('travel_request/', handle_manager_requests, name='manager_travel_requests_list'),  # List all pending requests
    path('travel_request/<int:id>/', handle_manager_requests, name='manager_travel_request_detail'),  # Handle specific request actions
]
