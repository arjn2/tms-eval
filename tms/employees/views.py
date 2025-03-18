from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from app_tms.models import Travel_Requests
from app_tms.serializers import TravelRequestsSerializer
from app_tms.permissions import IsEmployee
from app_tms.utils import (
    get_employee, can_edit_request, can_cancel_request,
    get_travel_requests_for_user, assign_manager_to_request,
    send_email_notification
)



# @api_view(['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
# @permission_classes([IsEmployee, IsAuthenticated])
# def handle_travel_request(request):
#     """
#     Function to handle various travel request actions based on HTTP methods and ids.
#     """
#     if request.method == 'POST':
#         create_travel_request(request)

#     elif request.method == 'GET':
#         if id is not None:
#             return get_travel_request(request, id)
#         return list_travel_requests(request)

#     elif request.method == 'PUT':
#         return update_travel_request(request, id)

#     elif request.method == 'DELETE':
#         return delete_travel_request(request, id)

#     elif request.method == 'PATCH':
#         action = request.data.get("action")
#         if action == "cancel":
#             return cancel_travel_request(request, id)
#         elif action == "respond":
#             return respond_to_request(request, id)

#     return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


# # link handling function
# @api_view(['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
# # @permission_classes([IsEmployee, IsAuthenticated])
# def handle_travel_request(request, id=None):
#     """
#     Function to handle various travel request actions based on HTTP methods and ids.
#     """
#     if request.method == 'POST':
#          create_travel_request(request)
#     elif request.method == 'GET':
#         return list_travel_requests(request)
#     elif request.method == 'GET':
#         return get_travel_request(request, id)
#     elif request.method == 'PUT':
#         return update_travel_request(request, id)
#     elif request.method == 'DELETE':
#         return delete_travel_request(request, id)
#     elif request.method == 'PATCH':
#         action = request.data.get("action")
#         if action == "cancel":
#             return cancel_travel_request(request, id)
#         elif action == "respond":
#             return respond_to_request(request, id)
#     return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Travel Requests ----------------
# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @permission_classes([IsEmployee, IsAuthenticated])
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
# @permission_classes([IsEmployee, IsAuthenticated])
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
# @permission_classes([IsEmployee, IsAuthenticated])
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
# @permission_classes([IsEmployee, IsAuthenticated])
# def cancel_travel_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_cancel_request(travel_request, request.user):
#         return Response({"error": "Cannot cancel this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.request_status = Travel_Requests.RequestStatusIndex.CANCELED
#     travel_request.save()
#     return Response({"message": "Request canceled."}, status=status.HTTP_200_OK)

# @api_view(['PATCH'])
# @permission_classes([IsEmployee, IsAuthenticated])
# def respond_to_request(request, id):
#     travel_request = get_object_or_404(Travel_Requests, id=id)
#     if not can_edit_request(travel_request, request.user):
#         return Response({"error": "Cannot respond to this request."}, status=status.HTTP_403_FORBIDDEN)
#     travel_request.additional_info = request.data.get('additional_info')
#     travel_request.save()
#     return Response({"message": "Response submitted."}, status=status.HTTP_200_OK)


# # # ----------------------------------------------------------------------------------------


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from app_tms.models import Travel_Requests
from app_tms.serializers import TravelRequestsSerializer,EmployeeSerializer
from app_tms.permissions import IsEmployee
from app_tms.utils import (
    get_employee, can_edit_request, can_cancel_request,
    get_travel_requests_for_user, assign_manager_to_request,
    send_email_notification
)
from rest_framework.authentication import TokenAuthentication


# @api_view(['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
@csrf_exempt
# @permission_classes([IsAuthenticated,IsEmployee])
def handle_travel_request(request, id=None):
    # serializer = TravelRequestsSerializer(data={**request.data, "employee": request.user.id})

    """
    Handle various travel request actions based on HTTP methods.
    - `POST`: Create a new travel request.
    - `GET`: Fetch travel requests (all or specific by ID).
    - `PUT`: Update a travel request (by ID).
    - `DELETE`: Delete a travel request (by ID).
    - `PATCH`: Perform actions (cancel/respond) on a travel request.
    """
    if request.method == 'POST':
        # print('hi')
        return create_travel_request(request)
        

    if request.method == 'GET':
        if id:
            return get_travel_request(request, id)
        return list_travel_requests(request)

    if request.method == 'PUT':
        return update_travel_request(request, id)

    if request.method == 'DELETE':
        return delete_travel_request(request, id)

    if request.method == 'PATCH':
        action = request.data.get("action")
        if action == "cancel":
            return cancel_travel_request(request, id)
        elif action == "respond":
            return respond_to_request(request, id)

    return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Travel Request Actions ----------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated,IsEmployee])
# def create_travel_request(request):
#     """
#     Employees can submit a new travel request.
#     """
#     employee = get_employee(request.user)
#     if not employee:
#         return Response({"error": "Employee not found."}, status=status.HTTP_400_BAD_REQUEST)
    
#     data = request.data.copy()
#     data['employee'] = employee.id
#     manager = assign_manager_to_request(employee)
#     data['manager'] = manager.id if manager else None  # Auto-assign manager

#     serializer = TravelRequestsSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         send_email_notification(employee, "Travel Request Submitted", "Your request has been submitted.")
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsEmployee])
def create_travel_request(request):
    try:
        # Assuming get_employee and assign_manager_to_request are defined elsewhere
        employee = get_employee(request.user)
        if not employee:
            return Response({"error": "Employee not found."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['employee'] = employee.id

        manager = assign_manager_to_request(employee)
        data['manager'] = manager.id if manager else None

        serializer = TravelRequestsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            send_email_notification(employee, "Travel Request Submitted", "Your request has been submitted.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([IsEmployee, IsAuthenticated])
def list_travel_requests(request):
    """
    List all travel requests for the logged-in employee.
    """
    requests = get_travel_requests_for_user(request.user)
    serializer = TravelRequestsSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsEmployee, IsAuthenticated])
def get_travel_request(request, id):
    """
    Fetch a specific travel request by ID.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)
    serializer = TravelRequestsSerializer(travel_request)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsEmployee, IsAuthenticated])
def update_travel_request(request, id):
    """
    Employees can update their travel request (if editable).
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)

    if not can_edit_request(travel_request, request.user):
        return Response({"error": "You are not allowed to edit this request."}, status=status.HTTP_403_FORBIDDEN)

    serializer = TravelRequestsSerializer(travel_request, data=request.data, partial=False)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsEmployee, IsAuthenticated])
def delete_travel_request(request, id):
    """
    Employees can delete their travel request (if allowed).
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)

    if not can_cancel_request(travel_request, request.user):
        return Response({"error": "You cannot delete this request."}, status=status.HTTP_403_FORBIDDEN)

    travel_request.delete()
    return Response({"message": "Travel request deleted."}, status=status.HTTP_204_NO_CONTENT)


# ---------------- Employee Actions ----------------

@api_view(['PATCH'])
@permission_classes([IsEmployee, IsAuthenticated])
def cancel_travel_request(request, id):
    """
    Employees can cancel their travel request if allowed.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)

    if not can_cancel_request(travel_request, request.user):
        return Response({"error": "Cannot cancel this request."}, status=status.HTTP_403_FORBIDDEN)

    travel_request.request_status = Travel_Requests.RequestStatusIndex.CANCELED
    travel_request.save()
    
    return Response({"message": "Request canceled."}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsEmployee, IsAuthenticated])
def respond_to_request(request, id):
    """
    Employees can respond to manager/admin queries by adding additional info.
    """
    travel_request = get_object_or_404(Travel_Requests, id=id)

    if not can_edit_request(travel_request, request.user):
        return Response({"error": "Cannot respond to this request."}, status=status.HTTP_403_FORBIDDEN)

    additional_info = request.data.get('additional_info')
    if not additional_info:
        return Response({"error": "Missing additional information."}, status=status.HTTP_400_BAD_REQUEST)

    travel_request.additional_info = additional_info
    travel_request.save()
    
    return Response({"message": "Response submitted."}, status=status.HTTP_200_OK)
