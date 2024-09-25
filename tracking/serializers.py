# tracking/serializers.py
from rest_framework import serializers
import re
from datetime import datetime

class TrackingNumberRequestSerializer(serializers.Serializer):
    origin_country_id = serializers.CharField(max_length=2)
    destination_country_id = serializers.CharField(max_length=2)
    weight = serializers.DecimalField(max_digits=6, decimal_places=3)
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField(max_length=255)
    customer_slug = serializers.SlugField(max_length=255)

    def validate_origin_country_id(self, value):
        if not re.match(r'^[A-Z]{2}$', value):
            raise serializers.ValidationError("Invalid origin_country_id. Must be 2 uppercase letters.")
        return value

    def validate_destination_country_id(self, value):
        if not re.match(r'^[A-Z]{2}$', value):
            raise serializers.ValidationError("Invalid destination_country_id. Must be 2 uppercase letters.")
        return value

    def validate_weight(self, value):
        try:
            weight = round(float(value), 3)
        except ValueError:
            raise serializers.ValidationError("Invalid weight format.")
        return weight
