from rest_framework import serializers
from .models import UserProfile, DegreeArea, User

class UserProfileSerializer(serializers.ModelSerializer):
    degree_area = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DegreeArea.objects.all()
    )
    is_complete = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "degree_area",
            "academic_id",
            "phone",
            "emergency_contact",
            "emergency_phone",
            "is_complete",
        ]

class UserSerializer(serializers.ModelSerializer):
    userProfile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "userProfile",
        ]

    def get_userProfile(self, obj):
        request = self.context.get("request")

        if not hasattr(obj, "userprofile"):
            return None

        return request.build_absolute_uri(
            f"/api/users/user-profile/{obj.id}/"
        )
