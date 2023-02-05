from rest_framework import serializers
from api.models import *

class Summary_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = "__all__"
        
class User_info_Serializers(serializers.ModelSerializer):
    class Meta:
        model = User_info
        fields = "__all__"
        
class FileSerializer(serializers.ModelSerializer):
    class Meta():
        model = File
        fields = ('file', 'timestamp')