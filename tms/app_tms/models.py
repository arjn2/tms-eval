from django.db import models

#import django defualt table auth_user
from django.contrib.auth.models import User

class Employees(models.Model):
    #fields
    middle_name=models.CharField(max_length=50)

    #dates
    dob=models.DateField()
    created_at=models.DateField(auto_now_add=True)

    #Status
    class PresentStatusIndex(models.TextChoices):
        PRESENT='PR','PRESENT'
        ABSENT='AB','ABSENT'
    present_status=models.CharField(
        max_length=20,
        choices=PresentStatusIndex.choices,
        default=PresentStatusIndex.PRESENT
    )

    #FK reference auth_user table login id
    
    login_auth = models.OneToOneField(User, on_delete=models.CASCADE)



class Managers(models.Model):

    #fields
    middle_name=models.CharField(max_length=50)

    #Dates
    dob=models.DateField()

    #Status
    class PresentStatusIndex(models.TextChoices):
        PRESENT='PR','PRESENT'
        ABSENT='AB','ABSENT'
    present_status=models.CharField(
        max_length=20,
        choices=PresentStatusIndex.choices,
        default=PresentStatusIndex.PRESENT
    )

    #FK reference auth_user table login id
    
    login_auth = models.OneToOneField(User, on_delete=models.CASCADE)



class Admins(models.Model):

    #fields
    middle_name=models.CharField(max_length=50)
 

    #Dates
    dob=models.DateField()

    #Status
    class PresentStatusIndex(models.TextChoices):
        PRESENT='PR','PRESENT'
        ABSENT='AB','ABSENT'
    present_status=models.CharField(
        max_length=20,
        choices=PresentStatusIndex.choices,
        default=PresentStatusIndex.PRESENT
    )

    #FK reference auth_user table login id
    
    login_auth = models.OneToOneField(User,on_delete=models.CASCADE)


class Travel_Requests(models.Model):
    #enum choices for request status
    #fields
    from_location=models.CharField(max_length=50)
    to_location=models.CharField(max_length=50)
    preferred_travel_mode=models.CharField(max_length=255)
    lodging_required=models.SmallIntegerField()
    #preferred_lodging_location = models.CharField(max_length=255, null=True, blank=True)
    additional_requests=models.CharField(max_length=255)
    travel_purpose=models.CharField(max_length=255)
    lodging_location=models.CharField(max_length=255,null=True)
    # requested_date=models.DateField()

    #dates
    date_from=models.DateField()
    date_to=models.DateField()
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    #status
    class RequestStatusIndex(models.TextChoices):
        IN_PROGRESS='IP','IN-PROGRESS'
        APPROVED='AP','APPROVED'
        REJECTED='RJ','REQUEST REJECTED'
        CANCELLED = 'CN', 'CANCELLED'


    request_status=models.CharField(
        max_length=20,
        choices=RequestStatusIndex.choices,
        default=RequestStatusIndex.IN_PROGRESS
    )
    class AliveStatusIndex(models.TextChoices):
        OPEN='OP','OPEN'
        CLOSED='CL','CLOSED'

    alive_status=models.CharField(
        max_length=20,
        choices=AliveStatusIndex.choices,
        default=AliveStatusIndex.OPEN
    )

    #FK
    employee=models.ForeignKey(Employees,on_delete=models.PROTECT)
    manager=models.ForeignKey(Managers,on_delete=models.PROTECT)



class Manager_Assignments(models.Model):

    #FK
    employee=models.ForeignKey(Employees,on_delete=models.PROTECT)
    manager=models.ForeignKey(Managers,on_delete=models.PROTECT)

    #dates
    assigned_at=models.DateField(auto_now_add=True)





class Notes(models.Model):
    note_text = models.CharField(max_length=255)

    # Foreign Keys
    request = models.ForeignKey(Travel_Requests, on_delete=models.PROTECT, null=True, blank=True)
    admin = models.ForeignKey(Admins, on_delete=models.PROTECT, null=True, blank=True)
    manager = models.ForeignKey(Managers, on_delete=models.PROTECT, null=True, blank=True)
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, blank=True)

    # Track who added the note (Admin or Manager)
    note_by = models.CharField(max_length=10, choices=[("ADMIN", "Admin"), ("MANAGER", "Manager")],null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True,null=True)







