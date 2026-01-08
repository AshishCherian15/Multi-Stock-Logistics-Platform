from rest_framework import serializers
from .models import StockListModel

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockListModel
        fields = '__all__'