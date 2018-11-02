from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator

class Airport(models.Model):
    name_ch = models.CharField(max_length=50, null=True)
    name_en = models.CharField(max_length=50, null=True)
    iata = models.CharField(
        max_length=3,
        validators=[MinLengthValidator(3)],
        unique=True
    )
    icao = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4)],
        null=True
    )
    nationality = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(2)],
        null=True
    )

    class Meta:
        db_table = 'airports'

class AirportWeather(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='weather_history')
    station_iata = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4)],
        unique=True
    )
    station_pos_lat = models.FloatField()
    station_pos_lon = models.FloatField()
    observe_time = models.DateTimeField()
    metar_text = models.TextField(null=True)
    metar_time = models.DateTimeField()
    wind_dir = models.IntegerField()
    wind_speed = models.IntegerField()
    visibility = models.IntegerField()
    ceiling = models.IntegerField()
    temperature = models.FloatField()
    desc_ch = models.CharField(max_length=50, null=True)
    desc_en = models.CharField(max_length=50, null=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'airport_weather'


class Airline(models.Model):
    name_ch = models.CharField(max_length=50, null=True)
    name_en = models.CharField(max_length=50, null=True)
    alias_ch = models.CharField(max_length=50, null=True)
    alias_en = models.CharField(max_length=50, null=True)
    iata = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(2)],
        unique=True
    )
    icao = models.CharField(
        max_length=3,
        validators=[MinLengthValidator(3)],
        null=True
    )
    email = models.EmailField(null=True)
    addr = models.TextField(null=True)
    phone = models.CharField(max_length=50, null=True)
    nationality = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(2)],
        null=True
    )

    class Meta:
        db_table = 'airlines'

class Flight(models.Model):
    airline = models.ForeignKey('Airline', on_delete=models.CASCADE, related_name='flights')
    airport_dept = models.ForeignKey('Airport', on_delete=models.CASCADE, related_name='departureflights')
    airport_dest = models.ForeignKey('Airport', on_delete=models.CASCADE, related_name='arrivalflights')
    flight_date = models.DateField()
    flight_no = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(1)],
        null=True
    )
    route_type = models.IntegerField(null=True)
    sched_dept_time = models.DateTimeField(null=True)
    actual_dept_time = models.DateTimeField(null=True)
    est_dept_time = models.DateTimeField(null=True)
    dept_remark = models.CharField(max_length=50, null=True)
    sched_arr_time = models.DateTimeField(null=True)
    actual_arr_time = models.DateTimeField(null=True)
    est_arr_time = models.DateTimeField(null=True)
    arr_remark = models.CharField(max_length=50, null=True)
    dept_terminal = models.CharField(max_length=10, null=True)
    arr_terminal = models.CharField(max_length=10, null=True)
    dept_gate = models.CharField(max_length=10, null=True)
    arr_gate = models.CharField(max_length=10, null=True)
    ac_type = models.CharField(max_length=20, null=True)
    baggage_claim = models.CharField(max_length=20, null=True)
    check_counter = models.CharField(max_length=20, null=True)
    is_cargo = models.BooleanField()
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flights'
        unique_together = (('flight_no', 'flight_date', 'airline'),)
