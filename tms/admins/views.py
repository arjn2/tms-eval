from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app_tms.models import Travel_Requests, Employees, Managers, Notes
from app_tms.serializers import (
    EmployeeSerializer, ManagerSerializer, TravelRequestsSerializer
)
from app_tms.permissions import IsAdmin
from app_tms.utils import create_user, send_email_notification, get_admin
from rest_framework.permissions import IsAuthenticated

#-------------function url handler--------------

@api_view(['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def handle_admin_requests(request, id=None):
    """
    Function to handle various admin actions related to travel requests, employees, and managers.
    """

    # Travel Request Actions
    if request.method == 'GET' and id:
        return get_travel_request_of_employee(request, id)
    elif request.method == 'GET':
        return list_all_requests(request)
    elif request.method == 'PATCH' and id:
        action = request.data.get("action")
        if action == "close":
            return close_travel_request(request, id)
        elif action == "send_note":
            return send_request_note(request, id)

    # Employee & Manager Actions
    elif request.method == 'POST':
        action = request.data.get("action")
        if action == "add_employee":
            return add_employee(request)
        elif action == "add_manager":
            return add_manager(request)
    elif request.method == 'GET' and request.query_params.get("type") == "employees":
        return list_employees(request)
    elif request.method == 'GET' and request.query_params.get("type") == "managers":
        return list_managers(request)

    return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)



# ---------------- Admin Actions ----------------

@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def close_travel_request(request, id):
    """
    Close travel request
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)
    travel_request.request_status = Travel_Requests.RequestStatusIndex.CLOSED
    travel_request.save()
    return Response({"message": "Request closed."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdmin, IsAuthenticated])
def list_all_requests(request):
    """
    List all requests
    """
    requests = Travel_Requests.objects.all()
    serializer = TravelRequestsSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdmin, IsAuthenticated])
def list_employees(request):
    """
    List all employees
    """
    employees = Employees.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdmin, IsAuthenticated])
def list_managers(request):
    """
    List all managers
    """
    managers = Managers.objects.all()
    serializer = ManagerSerializer(managers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAdmin, IsAuthenticated])
def add_employee(request):
    """
    Add a new employee
    """
    data = request.data.copy()
    response = create_user(
        data.pop("email"), data.pop("first_name"), data.pop("last_name"), "employee", data
    )
    return Response(response, status=status.HTTP_201_CREATED if response["success"] else status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAdmin, IsAuthenticated])
def add_manager(request):
    """
    Add a new manager
    """
    data = request.data.copy()
    response = create_user(
        data.pop("email"), data.pop("first_name"), data.pop("last_name"), "manager", data
    )
    return Response(response, status=status.HTTP_201_CREATED if response["success"] else status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAdmin, IsAuthenticated])
def send_request_note(request, id):
    """
    Admin can send a request note based on the travel request ID.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)
    admin = get_admin(request.user)

    if not admin:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    note_content = request.data.get("note", "").strip()
    if not note_content:
        return Response({"error": "Note content is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a note entry
    note = Notes.objects.create(
        travel_request=travel_request,
        admin=admin,
        note=note_content
    )

    # Send an email notification
    send_email_notification(
        travel_request.employee,
        "Admin Note Added",
        f"A note has been added to your travel request: {note_content}"
    )

    return Response({"message": "Request note sent successfully"}, status=status.HTTP_200_OK)



def get_travel_request_of_employee(request, id):
    """
    Admin function to fetch all travel requests of a specific employee.
    """
    try:
        employee = Employees.objects.get(id=id)
        travel_requests = Travel_Requests.objects.filter(employee=employee)

        if not travel_requests.exists():
            return Response({"message": "No travel requests found for this employee."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TravelRequestsSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Employees.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

