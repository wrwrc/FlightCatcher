from rest_framework import routers
from airports.api import AirlineViewSet, AirportViewSet, FlightViewSet

v1 = routers.DefaultRouter()
v1.register(r'airports', AirportViewSet)
v1.register(r'airlines', AirlineViewSet)
v1.register(r'flights', FlightViewSet)
