from rest_framework import serializers
from .models import ImageModel

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ('id', 'image', 'userid', 'command', 'created_at')