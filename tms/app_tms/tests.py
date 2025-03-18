import requests
import random
from django.contrib.auth import get_user_model
from app_tms.utils import create_admin, create_user
from app_tms.models import Manager_Assignments, Employees, Managers

User = get_user_model()
BASE_URL = "http://localhost:8000"

# Helper Function to Generate Random Password
def generate_random_password(username):
    return f"{username}@{random.randint(100, 999)}"

# Helper Function to Generate Unique Email
def generate_unique_email(base_email):
    count = 1
    new_email = base_email
    while User.objects.filter(email=new_email).exists():
        new_email = f"{base_email.split('@')[0]}{count}@example.com"
        count += 1
    return new_email

# Create Superuser if not exists
superuser_username = "su11"
superuser_password = "0"

if not User.objects.filter(username=superuser_username).exists():
    superuser = User.objects.create_superuser(
        username=superuser_username, password=superuser_password, email="su11@example.com"
    )
    print(" Superuser created successfully.")
else:
    superuser = User.objects.get(username=superuser_username)
    print("i Superuser already exists.")

# Create Admin User
admin_email = generate_unique_email("admin@example.com")
admin_password = generate_random_password("admin")

result = create_admin(
    email=admin_email,
    first_name="Admin",
    last_name="User",
    extra_data={"dob": "1990-01-01", "middle_name": "A"},
    created_by=superuser,
    password=admin_password
)
admin_user = User.objects.get(email=admin_email)
print(f" Admin Created - Username: {admin_user.username}, Password: {admin_password}")

# Create Employee User
emp1_email = generate_unique_email("emp1@example.com")
emp1_password = generate_random_password("emp1")

result = create_user(
    email=emp1_email,
    first_name="John",
    last_name="Doe",
    role="employee",
    extra_data={"dob": "1995-06-15", "middle_name": "B"},
    password=emp1_password
)
emp1_user = User.objects.get(email=emp1_email)
print(f" Employee Created - Username: {emp1_user.username}, Password: {emp1_password}")

# Create Manager User
manager_email = generate_unique_email("manager@example.com")
manager_password = generate_random_password("manager")

result = create_user(
    email=manager_email,
    first_name="Jane",
    last_name="Smith",
    role="manager",
    extra_data={"dob": "1985-02-20", "middle_name": "C"},
    password=manager_password
)
manager_user = User.objects.get(email=manager_email)
print(f" Manager Created - Username: {manager_user.username}, Password: {manager_password}")

# Validate Employee & Manager creation
try:
    emp1 = Employees.objects.get(login_auth=emp1_user)
    print(f" Employee {emp1_email} exists in Employees table.")
except Employees.DoesNotExist:
    print(f" ERROR: Employee {emp1_email} is missing in Employees table!")

try:
    manager = Managers.objects.get(login_auth=manager_user)
    print(f" Manager {manager_email} exists in Managers table.")
except Managers.DoesNotExist:
    print(f" ERROR: Manager {manager_email} is missing in Managers table!")

# Assign Employee to Manager
if not Manager_Assignments.objects.filter(employee=emp1).exists():
    Manager_Assignments.objects.create(employee=emp1, manager=manager)
    print(" Employee assigned to Manager.")
else:
    print(" Employee already assigned to a Manager.")

# Authenticate and Retrieve Token
def get_auth_token(username, password):
    """Authenticate and retrieve token for API requests using username."""
    login_data = {"username": username, "password": password}
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        response.raise_for_status()
        response_json = response.json()
        token = response_json.get("token")

        if token:
            print(f" Login successful for {username}.  Token: {token}")
            return {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        else:
            print(f" Login failed for {username}: No token received. Response: {response_json}")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f" HTTP error during login for {username}: {http_err} - Response: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f" Request error during login for {username}: {req_err}")
    except ValueError:
        print(f" Invalid JSON response during login for {username}. Response text: {response.text}")

    return None  

# Logout function
def logout(headers, username):
    """Logout user after setup."""
    try:
        response = requests.post(f"{BASE_URL}/logout/", headers=headers)
        response.raise_for_status()
        print(f" {username} logged out successfully.")
    except requests.exceptions.RequestException as e:
        print(f" Logout failed for {username}: {e}")

# Authenticate Superuser
su_headers = get_auth_token(superuser_username, superuser_password)
if not su_headers:
    print(" Stopping execution due to superuser authentication failure.")
    exit()
logout(su_headers, superuser_username)

# Authenticate Admin
admin_headers = get_auth_token(admin_user.username, admin_password)
if not admin_headers:
    print(" Stopping execution due to admin authentication failure.")
    exit()
logout(admin_headers, admin_user.username)

# Authenticate Employee
emp1_headers = get_auth_token(emp1_user.username, emp1_password)
if not emp1_headers:
    print(" Stopping execution due to employee authentication failure.")
    exit()
logout(emp1_headers, emp1_user.username)

# Authenticate Manager
manager_headers = get_auth_token(manager_user.username, manager_password)
if not manager_headers:
    print(" Stopping execution due to manager authentication failure.")
    exit()
logout(manager_headers, manager_user.username)

# travel request dummy json
travel_request_data = {
    "from_location": "Los Angeles",
    "to_location": "New York",
    "preferred_travel_mode": "Flight",
    "lodging_required": 1, 
    "preferred_lodging_location": "Hotel XYZ",
    "additional_requests": "Need a vegetarian meal",
    "travel_purpose": "Business Meeting",
    "date_from": "2025-04-10",
    "date_to": "2025-04-20"
}

