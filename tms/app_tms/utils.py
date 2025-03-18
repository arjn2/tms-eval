from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Employees, Managers, Admins, Travel_Requests, Manager_Assignments

from django.contrib.auth.models import User
from .serializers import EmployeeSerializer, ManagerSerializer, AdminSerializer
from django.db import transaction
from django.conf import settings
import random

logger = logging.getLogger(__name__)




# --------------- User Role Retrieval Functions ---------------

def get_employee(user):
    """
    Retrieves the employee object associated with the given user.

    Args:
        user (User): The authenticated user.

    Returns:
        Employees or None: The employee object if found, else None.
    """
    return Employees.objects.filter(login_auth=user).first()

def get_manager(user):
    """
    Retrieves the manager object associated with the given user.

    Args:
        user (User): The authenticated user.

    Returns:
        Managers or None: The manager object if found, else None.
    """
    return Managers.objects.filter(login_auth=user).first()

def get_admin(user):
    """
    Retrieves the admin object associated with the given user.

    Args:
        user (User): The authenticated user.

    Returns:
        Admins or None: The admin object if found, else None.
    """
    return Admins.objects.filter(login_auth=user).first()

# --------------- Travel Request Related Utility Functions ---------------

def get_travel_requests_for_user(user):
    """
    Retrieves travel requests based on the role of the authenticated user.

    Args:
        user (User): The authenticated user.

    Returns:
        QuerySet: A queryset of travel requests based on the user's role.
    """
    employee = get_employee(user)
    if employee:
        return Travel_Requests.objects.filter(employee=employee)

    manager = get_manager(user)
    if manager:
        return Travel_Requests.objects.filter(manager=manager)

    admin = get_admin(user)
    if admin:
        return Travel_Requests.objects.all()

    return Travel_Requests.objects.none()


from django.db.models import F
from random import choice

def assign_manager_to_request(employee):
    """
    Retrieves the assigned manager for an employee.
    If no assignment exists, assigns an existing manager.

    Args:
        employee (Employees): The employee object.

    Returns:
        Managers: The assigned or newly assigned manager.
    """
    assigned_manager = Manager_Assignments.objects.filter(
        employee=employee
    ).select_related('manager').first()

    if assigned_manager:
        return assigned_manager.manager  # Return the already assigned manager
    
    # If no manager assignment exists, find an existing manager
    existing_managers = Managers.objects.all()
    
    if existing_managers.exists():
        new_manager = choice(existing_managers)  # Assign a random manager
        Manager_Assignments.objects.create(employee=employee, manager=new_manager)
        return new_manager  # Return the newly assigned manager
    
    return None  # No managers available, return None



def can_edit_request(travel_request, user):
    """
    Checks if an employee can edit a travel request.

    Args:
        travel_request (Travel_Requests): The travel request object.
        user (User): The authenticated user.

    Returns:
        bool: True if the employee owns the request and it's still in progress, False otherwise.
    """
    employee = get_employee(user)
    return employee and travel_request.employee == employee and travel_request.request_status == Travel_Requests.RequestStatusIndex.IN_PROGRESS

def can_cancel_request(travel_request, user):
    """
    Checks if an employee can cancel a travel request.

    Args:
        travel_request (Travel_Requests): The travel request object.
        user (User): The authenticated user.

    Returns:
        bool: True if the request is owned by the employee and has not been approved or rejected, False otherwise.
    """
    employee = get_employee(user)
    return employee and travel_request.employee == employee and travel_request.request_status == Travel_Requests.RequestStatusIndex.IN_PROGRESS

def can_approve_or_reject(travel_request, user):
    """
    Checks if a manager can approve or reject a travel request.

    Args:
        travel_request (Travel_Requests): The travel request object.
        user (User): The authenticated user.

    Returns:
        bool: True if the request is assigned to the manager, False otherwise.
    """
    manager = get_manager(user)
    return manager and travel_request.manager == manager and travel_request.request_status == Travel_Requests.RequestStatusIndex.IN_PROGRESS

def can_request_more_info(travel_request, user):
    """
    Checks if an admin can request additional information for a travel request.

    Args:
        travel_request (Travel_Requests): The travel request object.
        user (User): The authenticated user.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    admin = get_admin(user)
    return admin is not None

def can_close_request(travel_request, user):
    """
    Checks if an admin can close an approved travel request.

    Args:
        travel_request (Travel_Requests): The travel request object.
        user (User): The authenticated user.

    Returns:
        bool: True if the request is approved and the user is an admin, False otherwise.
    """
    admin = get_admin(user)
    return admin is not None and travel_request.request_status == Travel_Requests.RequestStatusIndex.APPROVED

# --------------- Email Notification Utility Function ---------------

def send_email_notification(user, subject, message):
    """
    Sends an email notification to a specified user.
    

    Args:
        user (User): The recipient user object. The function retrieves the email from `user.login_auth.email`.
        subject (str): The subject of the email.
        message (str): The body of the email.

    Returns:
        None: The function sends the email but does not return a value.

    NB:using mailtrap credentials for testing
    # Looking to send emails in production? Check out our Email API/SMTP product!
    EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
    EMAIL_HOST_USER = '608f86c89ec892'
    EMAIL_HOST_PASSWORD = '********d93b'
    EMAIL_PORT = '2525'

    """

    '''
    
    recipient_email = user.login_auth.email
    '''

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender Email
            [user.login_auth.email],   # Recipient Email
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send email to {user.login_auth.email}: {e}")


# --------------------------------usercreation--------------------------------------


def generate_username(email):
    """Generate a unique username from email."""
    base_username = email.split('@')[0]
    counter = 1
    username = base_username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


logger = logging.getLogger(__name__)

def create_user(email, first_name, last_name, role, extra_data, password=None):
    """
    Creates a user in both `auth_user` and the respective role table (Employees or Managers).

    Args:
        email (str): User's email.
        first_name (str): First name.
        last_name (str): Last name.
        role (str): Either 'employee' or 'manager'.
        extra_data (dict): Additional data like DOB, middle name, etc.
        password (str, optional): User-defined password. If None, generates a random one.

    Returns:
        dict: Created user data or error message.
    """
    try:
        if check_email_exists(email):
            return {"success": False, "message": "User already exists"}
        
        username = generate_username(email)
        
        # Generate a random password if none is provided
        if not password:
            random_number = random.randint(100, 999)
            password = f"{username}@{random_number}"

        with transaction.atomic():  # Ensures rollback on failure
            user = User.objects.create_user(
                username=username, 
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                password=password
            )

            extra_data["login_auth"] = user.id  # Link `auth_user` entry

            serializer_class = EmployeeSerializer if role == "employee" else ManagerSerializer
            serializer = serializer_class(data=extra_data)

            if serializer.is_valid():
                serializer.save()
                return {
                    "success": True, 
                    "message": f"{role.capitalize()} created successfully.", 
                    "generated_password": password  # Return password if auto-generated
                }
            else:
                user.delete()  # Cleanup if validation fails
                logger.error(f"Validation failed for {role}: {serializer.errors}")
                return {"success": False, "errors": serializer.errors}

    except Exception as e:
        logger.error(f"Failed to create {role}: {str(e)}", exc_info=True)
        return {"success": False, "message": "Error creating user."}


# def create_user(email, first_name, last_name, role, extra_data):
#     """
#     Creates a user in both `auth_user` and the respective role table (Employees or Managers).

#     Args:
#         email (str): User's email.
#         first_name (str): First name.
#         last_name (str): Last name.
#         role (str): Either 'employee' or 'manager'.
#         extra_data (dict): Additional data like DOB, middle name, etc.

#     Returns:
#         dict: Created user data or error message.
#     """
#     try:
#         if check_email_exists(email):
#             return {"success": False, "message": "User already exists"}
        
#         username = generate_username(email)
#         password = "test@employee111" if role == "employee" else "test@manager111"
        
#         with transaction.atomic():  # Ensures rollback on failure
#             user = User.objects.create_user(
#                 username=username, 
#                 email=email, 
#                 first_name=first_name, 
#                 last_name=last_name, 
#                 password=password
#             )

#             extra_data["login_auth"] = user.id  # Link `auth_user` entry

#             serializer_class = EmployeeSerializer if role == "employee" else ManagerSerializer
#             serializer = serializer_class(data=extra_data)

#             if serializer.is_valid():
#                 serializer.save()
#                 return {"success": True, "message": f"{role.capitalize()} created successfully."}
#             else:
#                 user.delete()  # Cleanup if validation fails
#                 logger.error(f"Validation failed for {role}: {serializer.errors}")
#                 return {"success": False, "errors": serializer.errors}

#     except Exception as e:
#         logger.error(f"Failed to create {role}: {str(e)}", exc_info=True)
#         return {"success": False, "message": "Error creating user."}


    # ------------------------------create-admin-for-superuser------------------------
    


def create_admin(email, first_name, last_name, extra_data, created_by, password=None):
    """
    Creates an admin user in both `auth_user` and the `Admins` table.

    Args:
        email (str): Admin's email.
        first_name (str): First name.
        last_name (str): Last name.
        extra_data (dict): Additional data like DOB, middle name, etc.
        created_by (User): The user creating the admin (must be a superuser).
        password (str, optional): User-defined password. If None, generates a random one.

    Returns:
        dict: Success message or error details.
    """
    if not created_by.is_superuser:
        return {"success": False, "message": "Only superusers can create an admin."}

    try:
        if check_email_exists(email):
            return {"success": False, "message": "Admin already exists"}
        
        username = email.split('@')[0]  # Use email prefix as username
        
        # Generate a random password if none is provided
        if not password:
            random_number = random.randint(100, 999)
            password = f"{username}@{random_number}"

        with transaction.atomic():  # Ensures rollback on failure
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            extra_data["login_auth"] = user.id  # Link `auth_user` entry

            serializer = AdminSerializer(data=extra_data)

            if serializer.is_valid():
                serializer.save()
                return {
                    "success": True,
                    "message": "Admin created successfully.",
                    "generated_password": password  # Return password if auto-generated
                }
            else:
                user.delete()  # Cleanup if validation fails
                logger.error(f"Validation failed for admin: {serializer.errors}")
                return {"success": False, "errors": serializer.errors}

    except Exception as e:
        logger.error(f"Failed to create admin: {str(e)}", exc_info=True)
        return {"success": False, "message": "Error creating admin."}
    


    # -----------------------------email-existence-check--------------------------
def check_email_exists(email):
    """
    Checks whether the given email already exists in the `User` table.

    Args:
        email (str): The email to check.

    Returns:
        bool: True if the email exists, False otherwise.
    """
    return User.objects.filter(email=email).exists()


