from django.urls import path

from .problem_views import (
    problem_list,
    problem_detail,
    problem_create,
    problem_update,
    problem_delete,
)


from .service_views import (
    service_list,
    service_detail,
    service_create,
    service_update,
    service_delete,
)

from .workshop_service_views import (
    workshop_service_list,
    workshop_service_detail,
    workshop_service_create, workshop_service_update, workshop_service_delete,
)


urlpatterns = [
    path("problems/", problem_list),
    path("problems/<uuid:id>/", problem_detail),
    path("problems/create/", problem_create),
    path("problems/<uuid:id>/update/", problem_update),
    path("problems/<uuid:id>/delete/", problem_delete),
    path("services/", service_list),
    path("services/<uuid:id>/", service_detail),
    path("services/create/", service_create),
    path("services/<uuid:id>/update/", service_update),
    path("services/<uuid:id>/delete/", service_delete),
    path("workshop-services/",workshop_service_list,),
    path("workshop-services/<uuid:id>/",workshop_service_detail,),
    path( "workshop-services/create/",workshop_service_create,),
    path("workshop-services/<uuid:id>/update/",workshop_service_update,),
    path("workshop-services/<uuid:id>/delete/", workshop_service_delete,),
    ]




