from rest_framework import serializers
from .models import ListModel

class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListModel
        fields = '__all__'