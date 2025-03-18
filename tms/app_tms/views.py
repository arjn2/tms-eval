from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Travel_Requests, Employees, Managers, Admins, Notes
from .serializers import (EmployeeSerializer,ManagerAssignmentsSerializer,ManagerSerializer
                          ,AdminSerializer,NotesSerializer,TravelRequestsSerializer,UserSerializer)
from .permissions import IsEmployee, IsManager, IsAdmin
from .utils import (
    get_employee, get_manager, get_admin, get_travel_requests_for_user,
    can_edit_request, can_cancel_request, can_approve_or_reject,
    can_request_more_info, can_close_request, assign_manager_to_request,
    send_email_notification,create_user
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes

# ---------------- Authentication ----------------


# @csrf_exempt
@api_view(['POST'])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    
    if user:
        # Generate or get existing token
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "Login successful.", "token": token.key}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

# # ---------------- Travel Requests ----------------
# @api_view(['POST'])
# @permission_classes([IsEmployee,IsAuthenticated])
# def create_travel_request(request):
#     employee = get_employee(request.user)
#     if not employee:
#         return Response({"error": "Employee not found."}, status=status.HTTP_400_BAD_REQUEST)
    
#     data = request.data.copy()
#     data['employee'] = employee.id
#     data['manager'] = assign_manager_to_request(employee).id if assign_manager_to_request(employee) else None
    
#     serializer = TravelRequestsSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         send_email_notification(employee, "Travel Request Submitted", "Your request has been submitted.")
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_travel_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     serializer = TravelRequestsSerializer(travel_request)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['PUT'])
# @permission_classes([IsEmployee,IsAuthenticated])
# def update_travel_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_edit_request(travel_request, request.user):
#         return Response({"error": "You are not allowed to edit this request."}, status=status.HTTP_403_FORBIDDEN)
    
#     serializer = TravelRequestsSerializer(travel_request, data=request.data, partial=False)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['DELETE'])
# @permission_classes([IsEmployee,IsAuthenticated])
# def delete_travel_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_cancel_request(travel_request, request.user):
#         return Response({"error": "You cannot delete this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.delete()
#     return Response({"message": "Travel request deleted."}, status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_travel_requests(request):
#     requests = get_travel_requests_for_user(request.user)
#     serializer = TravelRequestsSerializer(requests, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# # ---------------- Employee Actions ----------------
# @api_view(['PATCH'])
# @permission_classes([IsEmployee,IsAuthenticated])
# def cancel_travel_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_cancel_request(travel_request, request.user):
#         return Response({"error": "Cannot cancel this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.request_status = Travel_Requests.RequestStatusIndex.CANCELED
#     travel_request.save()
#     return Response({"message": "Request canceled."}, status=status.HTTP_200_OK)

# @api_view(['PATCH'])
# @permission_classes([IsEmployee,IsAuthenticated])
# def respond_to_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_edit_request(travel_request, request.user):
#         return Response({"error": "Cannot respond to this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.additional_info = request.data.get('additional_info')
#     travel_request.save()
#     return Response({"message": "Response submitted."}, status=status.HTTP_200_OK)

# # ---------------- Manager Actions ----------------
# @api_view(['PATCH'])
# @permission_classes([IsManager,IsAuthenticated])
# def approve_travel_request(request, id):
#     """
#     Approve travel request
#     """
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_approve_or_reject(travel_request, request.user):
#         return Response({"error": "Cannot approve this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.request_status = Travel_Requests.RequestStatusIndex.APPROVED
#     travel_request.save()
#     return Response({"message": "Request approved."}, status=status.HTTP_200_OK)

# @api_view(['PATCH'])
# @permission_classes([IsManager,IsAuthenticated])
# def reject_travel_request(request, id):
#     """
#     Reject travel request
#     """
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_approve_or_reject(travel_request, request.user):
#         return Response({"error": "Cannot reject this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.request_status = Travel_Requests.RequestStatusIndex.REJECTED
#     travel_request.save()
#     return Response({"message": "Request rejected."}, status=status.HTTP_200_OK)

# # ---------------- Admin Actions ----------------
# @api_view(['PATCH'])
# @permission_classes([IsAdmin,IsAuthenticated])
# def close_travel_request(request, id):
#     """
#     Close travel request
#     """
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_close_request(travel_request, request.user):
#         return Response({"error": "Cannot close this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.request_status = Travel_Requests.RequestStatusIndex.CLOSED
#     travel_request.save()
#     return Response({"message": "Request closed."}, status=status.HTTP_200_OK)

# @api_view(['GET'])
# @permission_classes([IsAdmin,IsAuthenticated])
# def list_all_requests(request):
#     """
#     List all requests
#     """
#     requests = Travel_Requests.objects.all()
#     serializer = TravelRequestsSerializer(requests, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)



# # ---- List All Managers ----
# @api_view(['GET'])
# @permission_classes([IsAdmin,IsAuthenticated])
# def list_employees(request):
#     employees = Employees.objects.all()
#     serializer = EmployeeSerializer(employees, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)



# # ---- List All Managers ----
# @api_view(["GET"])
# @permission_classes([IsAdmin,IsAuthenticated])
# def list_managers(request):
#     """
#     Admin can view all managers.
#     """
#     managers = Managers.objects.all()
#     serializer = ManagerSerializer(managers, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)



# @api_view(["POST"])
# @permission_classes([IsAdmin,IsAuthenticated])
# # @authentication_classes([TokenAuthentication])
# def add_employee(request):
#     """
#     Adds a new employee.

#     """
#     data = request.data.copy()
#     response = create_user(data.pop("email"), data.pop("first_name"), data.pop("last_name"), "employee", data)
#     return Response(response, status=status.HTTP_201_CREATED if response["success"] else status.HTTP_400_BAD_REQUEST)

# @api_view(["POST"])
# @permission_classes([IsAdmin,IsAuthenticated])
# # @authentication_classes([TokenAuthentication])
# def add_manager(request):
#     """
#     Adds a new manager.

#     Expected JSON:
#     {
#         "email": "manager@example.com",
#         "first_name": "Alice",
#         "last_name": "Smith",
#         "dob": "1985-05-10",
#         "middle_name": "L",
#     }
    
#     """
#     data = request.data.copy()
#     response = create_user(data.pop("email"), data.pop("first_name"), data.pop("last_name"), "manager", data)
#     return Response(response, status=status.HTTP_201_CREATED if response["success"] else status.HTTP_400_BAD_REQUEST)





# # --------------------------------------------------------------------------------------------------------

# @api_view(["GET"])
# @permission_classes([IsManager,IsAuthenticated])
# def list_pending_requests(request):
#     """
#     Lists all pending travel requests assigned to the authenticated manager.
#     """
#     manager = get_manager(request.user)
#     if not manager:
#         return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

#     pending_requests = Travel_Requests.objects.filter(manager=manager, request_status=Travel_Requests.RequestStatusIndex.IN_PROGRESS)
#     serializer = TravelRequestsSerializer(pending_requests, many=True)
    
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(["PATCH"])
# @permission_classes([IsManager, IsAdmin, IsAuthenticated])
# def request_more_info(request, id):
#     """
#     Allows a manager or admin to request additional information from an employee.
#     Adds a note and sends an email notification.
#     """
#     try:
#         travel_request = Travel_Requests.objects.get(id=id)
#     except Travel_Requests.DoesNotExist:
#         return Response({"error": "Travel request not found"}, status=status.HTTP_404_NOT_FOUND)

#     user = request.user
#     manager = get_manager(user)
#     admin = get_admin(user)

#     if not (manager or admin):
#         return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

#     note_content = request.data.get("note", "").strip()
#     if not note_content:
#         return Response({"error": "Note content is required"}, status=status.HTTP_400_BAD_REQUEST)

#     # Create a note entry
#     note = Notes.objects.create(
#         travel_request=travel_request,
#         manager=manager if manager else None,
#         admin=admin if admin else None,
#         note=note_content
#     )

#     # Send an email notification
#     send_email_notification(
#         travel_request.employee,
#         "Additional Information Required",
#         f"Your travel request requires more information: {note_content}"
#     )

#     return Response({"message": "Request for more info sent successfully"}, status=status.HTTP_200_OK)

# @api_view(["POST"])
# @permission_classes([IsManager, IsAdmin, IsAuthenticated])
# def add_note(request, id):
#     """
#     Allows a manager or admin to add a note to a travel request.
#     """
#     try:
#         travel_request = Travel_Requests.objects.get(id=id)
#     except Travel_Requests.DoesNotExist:
#         return Response({"error": "Travel request not found"}, status=status.HTTP_404_NOT_FOUND)

#     user = request.user
#     manager = get_manager(user)
#     admin = get_admin(user)

#     if not (manager or admin):
#         return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

#     note_content = request.data.get("note", "").strip()
#     if not note_content:
#         return Response({"error": "Note content is required"}, status=status.HTTP_400_BAD_REQUEST)

#     # Create a note entry
#     note = Notes.objects.create(
#         travel_request=travel_request,
#         manager=manager if manager else None,
#         admin=admin if admin else None,
#         note=note_content
#     )

#     return Response({"message": "Note added successfully"}, status=status.HTTP_201_CREATED)
