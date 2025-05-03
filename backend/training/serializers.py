from rest_framework import serializers
from .models import User,DailySession,TrackingLocation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class TrackingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingLocation
        fields = '__all__'

class DailySessionSerializer(serializers.ModelSerializer):
    locations = TrackingLocationSerializer(many=True, read_only=True)
    class Meta:
        model = DailySession
        fields = '__all__'