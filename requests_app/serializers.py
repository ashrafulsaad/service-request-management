from rest_framework import serializers

from accounts.models import User
from .models import Category, ServiceRequest, Comment, Attachment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = "__all__"

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()

        request = self.context.get("request")

        # Citizen cannot change these fields
        extra_kwargs.setdefault("citizen", {})["read_only"] = True

        if request and request.user.is_authenticated:
            if request.user.role == "citizen":
                extra_kwargs.setdefault("status", {})["read_only"] = True
                extra_kwargs.setdefault(
                    "assigned_officer", {}
                )["read_only"] = True

        return extra_kwargs


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    MAX_FILE_SIZE = 5 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".doc",
        ".docx",
    }

    class Meta:
        model = Attachment
        fields = "__all__"
        read_only_fields = [
            "request",
            "uploaded_by",
            "uploaded_at",
        ]

    def validate_file(self, value):
        import os

        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File size cannot exceed 5 MB."
            )

        extension = os.path.splitext(value.name)[1].lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Unsupported file type."
            )

        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
        ]
