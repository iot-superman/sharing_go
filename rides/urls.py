from django.urls import path
from . import views
urlpatterns=[
 path('health/',views.health), path('reverse-geocode/',views.reverse_geocode), path('geocode/',views.forward_geocode), path('route/',views.route_preview), path('me/',views.me), path('rides/',views.rides), path('rides/<int:ride_id>/',views.ride_detail),
 path('rides/<int:ride_id>/join/',views.join_ride), path('rides/<int:ride_id>/cancel/',views.cancel_ride),
 path('rides/<int:ride_id>/messages/',views.messages), path('rides/<int:ride_id>/locations/',views.locations),
 path('my-trip/',views.my_trip),
]
