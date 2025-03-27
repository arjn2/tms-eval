
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from app_tms.models import Travel_Requests,Notes
from app_tms.serializers import TravelRequestsSerializer,EmployeeSerializer,TravelRequestsUpdateSerializer,NotesSerializer
from app_tms.permissions import IsEmployee
from app_tms.utils import (
    get_employee, can_edit_request, can_cancel_request,
    get_travel_requests_for_user, assign_manager_to_request,
    send_email_notification
)
from rest_framework.authentication import TokenAuthentication
import traceback

# ----------------------------------------------------------------------------------------

def handle_travel_request(request, id=None):

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
        return cancel_travel_request(request, id)
    

    return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsEmployee])
def create_travel_request(request):
    try:
        # Assuming get_employee and assign_manager_to_request are defined elsewhere
        employee = get_employee(request.user)
        if not employee:
            return Response({"error": "Employee not found."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        print(f"DEBUG - Employee type: {type(employee)}, ID: {employee.id}")
        data['employee'] = employee.id

        print(f"DEBUG - Raw request data before serialization: {data}")
        serializer = TravelRequestsSerializer(data=data)
        
        if serializer.is_valid():
            print(f"DEBUG - Employee in validated_data: {type(serializer.validated_data.get('employee'))}")
            print(f"DEBUG - Employee in original data: {type(data['employee'])}")
            travel_request = serializer.save()
            print(f"DEBUG - Travel Request Data: {data}")
            print(f"DEBUG - Validated Data: {serializer.validated_data}")
            # try:
            #     send_email_notification(employee, "Travel Request Submitted", "Your request has been submitted.")
            # except Exception as e:
            #     print("Error sending email:", str(e))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        print(f"Request data: {request.data}")
        return Response({
            "error": str(e),
            "exception_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
    

    serializer = TravelRequestsUpdateSerializer(travel_request, data=request.data, partial=False)
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

    travel_request.request_status = Travel_Requests.RequestStatusIndex.CANCELLED
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

# -----------------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsEmployee, IsAuthenticated])
def read_notes(request, id):
    """
    Fetch all notes related to a specific travel request by ID.
    """
    notes = Notes.objects.filter(request_id=id)  # Get notes for the given travel request ID
    if not notes.exists():
        return Response({"message": "No notes found for this travel request."}, status=status.HTTP_200_OK)

    serializer = NotesSerializer(notes, many=True)  # Serialize all notes
    return Response(serializer.data, status=status.HTTP_200_OK)