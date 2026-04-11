from rest_framework import serializers
from .models import Sport, Equipment, EquipmentBooking, Turf, TurfBooking


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'


class EquipmentBookingSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.equipment_name', read_only=True)

    class Meta:
        model = EquipmentBooking
        fields = '__all__'
        extra_kwargs = {
            'student': {'required': False, 'allow_null': True},
            'approved_by': {'required': False, 'allow_null': True},
            'status': {'required': False},
        }


class TurfSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = Turf
        fields = '__all__'


class TurfBookingSerializer(serializers.ModelSerializer):
    turf_name = serializers.CharField(source='turf.turf_name', read_only=True)

    class Meta:
        model = TurfBooking
        fields = '__all__'
        extra_kwargs = {
            'student': {'required': False, 'allow_null': True},
            'approved_by': {'required': False, 'allow_null': True},
            'status': {'required': False},
        }
