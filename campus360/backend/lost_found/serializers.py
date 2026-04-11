from rest_framework import serializers
from .models import LostFoundItem, Claim


class LostFoundItemSerializer(serializers.ModelSerializer):
    # Add read-only aliases matching what the frontend expects
    image = serializers.CharField(source='image_url', read_only=True)
    date = serializers.DateField(source='item_date', read_only=True)

    class Meta:
        model = LostFoundItem
        fields = '__all__'
        extra_kwargs = {
            'reporter': {'required': False, 'allow_null': True},
        }


class ClaimSerializer(serializers.ModelSerializer):
    item_details = LostFoundItemSerializer(source='item', read_only=True)
    claimant_email = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = '__all__'
        extra_kwargs = {
            'claimant': {'required': False, 'allow_null': True},
            'reviewed_by': {'required': False, 'allow_null': True},
        }

    def get_claimant_email(self, obj):
        try:
            return obj.claimant.email if obj.claimant else None
        except Exception:
            return None
