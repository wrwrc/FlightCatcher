from rest_framework import viewsets, serializers
from .models import Airline, Airport, Flight

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class AirlineSerializer(serializers.ModelSerializer):
    #flights = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Airline
        fields = '__all__'

class AirportSerializer(serializers.ModelSerializer):
    #flights = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Airport
        fields = '__all__'

class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

class AirlineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    filter_fields = ('iata',)

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_fields = ('iata',)
