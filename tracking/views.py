# tracking/views.py
import uuid
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TrackingNumberRequestSerializer
from rest_framework import status
from django.core.cache import cache  # Import Django cache framework
from datetime import datetime

class TrackingNumberGenerator(APIView):
    def get(self, request):
        serializer = TrackingNumberRequestSerializer(data=request.query_params)

        # Validate the input parameters
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If valid, proceed with tracking number generation
        validated_data = serializer.validated_data
        origin_country_id = validated_data.get('origin_country_id')
        destination_country_id = validated_data.get('destination_country_id')
        weight = validated_data.get('weight')
        customer_id = validated_data.get('customer_id')
        customer_name = validated_data.get('customer_name')
        customer_slug = validated_data.get('customer_slug')

        # Create a unique cache key based on request parameters
        cache_key = f"tracking_{origin_country_id}_{destination_country_id}_{weight}_{customer_id}_{customer_slug}"
        
        # Check if the tracking number is in the cache
        cached_tracking_number, cached_created_at = cache.get(cache_key, "%").split("%")
        
        if cached_tracking_number:
            # If found in cache, return the cached tracking number and creation time
            return Response({
                'tracking_number': cached_tracking_number,
                'created_at': cached_created_at
            })

        # Generate a short UUID-based tracking number
        base_uuid = uuid.uuid4()
        short_uuid = str(base_uuid).replace('-', '')[:12].upper()

        # Combine with a deterministic portion based on slug and countries
        tracking_number = f"{short_uuid[:8]}{origin_country_id}{destination_country_id}"

        # Store the tracking number in the cache
        cache.set(cache_key, tracking_number + "%" + datetime.now().isoformat(), timeout=86400)  # Cache for 1 day (or set timeout as needed)

        response_data = {
            "tracking_number": tracking_number,
            "created_at": datetime.now().isoformat()
        }

        return Response(response_data)
