from rest_framework import serializers
from api.models import *

class SummarySerializers(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = "__all__"
        
class User_infoSerializers(serializers.ModelSerializer):
    class Meta:
        model = User_info
        fields = "__all__"