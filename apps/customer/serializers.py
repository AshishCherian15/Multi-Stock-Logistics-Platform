from rest_framework import serializers
from .models import ListModel

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListModel
        fields = '__all__'