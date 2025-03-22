from rest_framework import serializers
from django.utils.timezone import now
from .models import Employees,Managers,Admins,Manager_Assignments,Notes,Travel_Requests

#default auth_user table
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'


class EmployeeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # exit
        # print(now().date())
        validated_data["created_at"] = now().date()
        return super().create(validated_data)
        
    # def validat
    class Meta:
        model=Employees
        fields='__all__'
        # read_only_fields = ("created_at",)
        # fields=['name','price']

class AdminSerializer(serializers.ModelSerializer):
    def validate_login_auth(self, value):
        if not isinstance(value, User):
            print(f" Invalid login_auth detected in serializer: {value} (Type: {type(value)})")
        return value
    class Meta:
        model=Admins
        fields='__all__'


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Managers
        fields='__all__'

class ManagerAssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Manager_Assignments
        fields='__all__'



class TravelRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel_Requests
        fields = "__all__"
        read_only_fields = ("created_at",)


class TravelRequestsUpdateSerializer(serializers.ModelSerializer):
    """
    serializer for update travel-request
    manager id , employee id is prevented from updating.
    """
    class Meta:
        model = Travel_Requests
        fields = '__all__'
        read_only_fields = ['manager', 'employee'] 

class NotesSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["created_at"] = now().date()
        return super().create(validated_data)

    class Meta:
        model = Notes
        fields = "__all__"
        read_only_fields = ("created_at",)
