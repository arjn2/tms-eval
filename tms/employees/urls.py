from django.urls import path
from .views import handle_travel_request,create_travel_request

urlpatterns = [
    path('travel-request/', handle_travel_request, name='travel_request_list_create'),
    path('travel-request/<int:id>/', handle_travel_request, name='travel_request_detail'),
]
