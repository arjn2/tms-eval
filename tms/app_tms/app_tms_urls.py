from django.urls import path
from . import views as vw

urlpatterns = [
    # Authentication
    path("login/", vw.login_user, name="login"),
    path("logout/", vw.logout_user, name="logout")

    # # Travel Requests
    # path("travel_request/", vw.create_travel_request, name="create_travel_request"),  # POST
    # path("travel_request/<int:id>/", vw.get_travel_request, name="get_travel_request"),  # GET
    # path("travel_request/<int:id>/update/", vw.update_travel_request, name="update_travel_request"),  # PUT
    # path("travel_request/<int:id>/delete/", vw.delete_travel_request, name="delete_travel_request"),  # DELETE
    # path("travel_requests/", vw.list_travel_requests, name="list_travel_requests"),  # GET

    # # Employee Actions
    # path("travel_request/<int:id>/cancel/", vw.cancel_travel_request, name="cancel_travel_request"),  # PATCH
    # path("travel_request/<int:id>/respond/", vw.respond_to_request, name="respond_to_request"),  # PATCH

    # # Manager Actions
    # path("travel_requests/pending/", vw.list_pending_requests, name="list_pending_requests"),  # GET (Filter pending requests)
    # path("travel_request/<int:id>/approve/", vw.approve_travel_request, name="approve_travel_request"),  # PATCH
    # path("travel_request/<int:id>/reject/", vw.reject_travel_request, name="reject_travel_request"),  # PATCH
    # path("travel_request/<int:id>/request_info/", vw.request_more_info, name="request_more_info"),  # PATCH
    # path("travel_request/<int:id>/add_note/", vw.add_note, name="add_note"),  # POST

    # # Admin Actions
    # path("employees/", vw.list_employees, name="list_employees"),  # GET
    # path("managers/", vw.list_managers, name="list_managers"),  # GET
    # path("travel_requests/all/", vw.list_all_requests, name="list_all_requests"),  # GET
    # # path("travel_request/<int:id>/process/", vw.process_travel_request, name="process_travel_request"),  # PATCH
    # path("travel_request/<int:id>/close/", vw.close_travel_request, name="close_travel_request"),  # PATCH
    # path("add_employee/", vw.add_employee, name="add_employee"),  # POST
    # path("add_manager/", vw.add_manager, name="add_manger"),  # POST


]

