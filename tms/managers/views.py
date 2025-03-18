
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app_tms.models import Travel_Requests, Notes
from app_tms.serializers import TravelRequestsSerializer
from app_tms.permissions import IsManager
from rest_framework.permissions import IsAuthenticated
from app_tms.utils import get_manager, can_approve_or_reject, send_email_notification


# @api_view(['GET', 'PATCH', 'POST'])
@permission_classes([IsManager, IsAuthenticated])
def handle_manager_requests(request, id=None):
    """
    Handles various manager actions based on HTTP methods.
    """

    # --------------------- Handle GET requests ---------------------
    if request.method == 'GET':
        if id:
            return get_travel_request(request, id)  # Get details of a specific request
        return list_pending_requests(request)  # List all pending requests for the manager

    # --------------------- Handle PATCH requests ---------------------
    elif request.method == 'PATCH':
        if not id:
            return Response({"error": "Travel request ID is required for this action."}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get("action")
        if not action:
            return Response({"error": "Action parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        if action == "approve":
            return approve_travel_request(request, id)
        elif action == "reject":
            return reject_travel_request(request, id)
        elif action == "request_info":
            return request_more_info(request, id)
        else:
            return Response({"error": "Invalid action specified."}, status=status.HTTP_400_BAD_REQUEST)

    # --------------------- Handle POST requests ---------------------
    elif request.method == 'POST':
        if not id:
            return Response({"error": "Travel request ID is required to add a note."}, status=status.HTTP_400_BAD_REQUEST)
        return add_note(request, id)

    return Response({"error": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# ---------------------------------------------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsManager, IsAuthenticated])
def approve_travel_request(request, id):
    """
    Approve travel request.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)
    if not can_approve_or_reject(travel_request, request.user):
        return Response({"error": "Cannot approve this request."}, status=status.HTTP_403_FORBIDDEN)
    
    travel_request.request_status = Travel_Requests.RequestStatusIndex.APPROVED
    travel_request.save()

    send_email_notification(travel_request.employee, "Travel Request Approved", "Your request has been approved.")
    
    return Response({"message": "Request approved."}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsManager, IsAuthenticated])
def reject_travel_request(request, id):
    """
    Reject travel request.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)
    if not can_approve_or_reject(travel_request, request.user):
        return Response({"error": "Cannot reject this request."}, status=status.HTTP_403_FORBIDDEN)
    
    travel_request.request_status = Travel_Requests.RequestStatusIndex.REJECTED
    travel_request.save()

    send_email_notification(travel_request.employee, "Travel Request Rejected", "Your request has been rejected.")
    
    return Response({"message": "Request rejected."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsManager, IsAuthenticated])
def list_pending_requests(request):
    """
    Lists all pending travel requests assigned to the authenticated manager.
    """
    manager = get_manager(request.user)
    if not manager:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    pending_requests = Travel_Requests.objects.filter(manager=manager, request_status=Travel_Requests.RequestStatusIndex.IN_PROGRESS)
    serializer = TravelRequestsSerializer(pending_requests, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@permission_classes([IsManager, IsAuthenticated])
def request_more_info(request, id):
    """
    Allows a manager to request additional information from an employee.
    Adds a note and sends an email notification.
    """
    try:
        travel_request = Travel_Requests.objects.get(id=id)
    except Travel_Requests.DoesNotExist:
        return Response({"error": "Travel request not found"}, status=status.HTTP_404_NOT_FOUND)

    manager = get_manager(request.user)
    if not manager:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    note_content = request.data.get("note", "").strip()
    if not note_content:
        return Response({"error": "Note content is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a note entry
    Notes.objects.create(
        travel_request=travel_request,
        manager=manager,
        note=note_content
    )

    # Send an email notification
    send_email_notification(
        travel_request.employee,
        "Additional Information Required",
        f"Your travel request requires more information: {note_content}"
    )

    return Response({"message": "Request for more info sent successfully"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsManager, IsAuthenticated])
def add_note(request, id):
    """
    Allows a manager to add a note to a travel request.
    """
    try:
        travel_request = Travel_Requests.objects.get(id=id)
    except Travel_Requests.DoesNotExist:
        return Response({"error": "Travel request not found"}, status=status.HTTP_404_NOT_FOUND)

    manager = get_manager(request.user)
    if not manager:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    note_content = request.data.get("note", "").strip()
    if not note_content:
        return Response({"error": "Note content is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a note entry
    Notes.objects.create(
        travel_request=travel_request,
        manager=manager,
        note=note_content
    )

    return Response({"message": "Note added successfully"}, status=status.HTTP_201_CREATED)


def get_travel_request(request, id):
    """
    Fetches a specific travel request for the manager.
    Ensures the request belongs to an employee assigned to this manager.
    """
    try:
        travel_request = Travel_Requests.objects.get(id=id, assigned_manager=request.user.managers)
    except Travel_Requests.DoesNotExist:
        return Response({"error": "Travel request not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TravelRequestsSerializer(travel_request)
    return Response(serializer.data, status=status.HTTP_200_OK)
