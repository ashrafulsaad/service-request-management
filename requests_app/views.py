from django.db.models import Count
from accounts.models import User
from rest_framework.views import APIView

from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import Category, ServiceRequest, Comment, Attachment
from .serializers import (
    CategorySerializer,
    ServiceRequestSerializer,
    CommentSerializer,
    AttachmentSerializer,
    UserSerializer,
)
from .permissions import IsAdmin, ServiceRequestPermission
from .filters import ServiceRequestFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()

        try:
            category.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This category cannot be deleted because "
                        "it is being used by one or more service requests."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all()

        role = self.request.query_params.get("role")

        if role:
            queryset = queryset.filter(role=role)

        return queryset

class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):

        total = ServiceRequest.objects.count()

        status_counts = (
            ServiceRequest.objects
            .values("status")
            .annotate(count=Count("id"))
        )

        priority_counts = (
            ServiceRequest.objects
            .values("priority")
            .annotate(count=Count("id"))
        )

        category_counts = (
            ServiceRequest.objects
            .values("category__name")
            .annotate(count=Count("id"))
        )

        officer_counts = (
            ServiceRequest.objects
            .filter(assigned_officer__isnull=False)
            .values("assigned_officer__username")
            .annotate(count=Count("id"))
        )

        unassigned = ServiceRequest.objects.filter(
            assigned_officer__isnull=True
        ).count()

        return Response({
            "total": total,

            "by_status": {
                item["status"]: item["count"]
                for item in status_counts
            },

            "by_priority": {
                item["priority"]: item["count"]
                for item in priority_counts
            },

            "by_category": {
                item["category__name"]: item["count"]
                for item in category_counts
            },

            "requests_per_officer": {
                item["assigned_officer__username"]: item["count"]
                for item in officer_counts
            },

            "unassigned": unassigned,
        })


class ServiceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [ServiceRequestPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ServiceRequestFilter

    search_fields = ["title"]

    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return ServiceRequest.objects.all()

        if user.role == "officer":
            return ServiceRequest.objects.filter(
                assigned_officer=user
            )

        return ServiceRequest.objects.filter(
            citizen=user
        )

    def perform_create(self, serializer):
        serializer.save(citizen=self.request.user)

    def update(self, request, *args, **kwargs):
        if request.user.role == "officer":
            allowed_fields = {"status"}

            if not set(request.data.keys()).issubset(allowed_fields):
                return Response(
                    {"detail": "Officers can only update status."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        if request.user.role != "admin":
            return Response(
                {"detail": "Only admins can assign officers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        service_request = self.get_object()

        officer_id = request.data.get("officer_id")

        if not officer_id:
            return Response(
                {"detail": "officer_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            officer = User.objects.get(
                id=officer_id,
                role="officer",
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Selected user is not an officer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service_request.assigned_officer = officer
        service_request.save()

        return Response({
            "detail": "Officer assigned successfully.",
            "officer": officer.username,
        })

    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        if request.user.role not in ["officer", "admin"]:
            return Response(
                {
                    "detail": (
                        "Only officers and admins can change status."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        service_request = self.get_object()

        new_status = request.data.get("status")

        allowed_statuses = {
            "pending",
            "in_progress",
            "resolved",
            "rejected",
        }

        if new_status not in allowed_statuses:
            return Response(
                {
                    "detail": "Invalid status.",
                    "allowed_statuses": list(allowed_statuses),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        service_request.status = new_status
        service_request.save()

        return Response({
            "detail": "Status updated successfully.",
            "status": service_request.status,
        })

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="comments",
    )
    def comments(self, request, pk=None):
        service_request = self.get_object()
        user = request.user

        is_related = (
            user.role == "admin"
            or service_request.citizen == user
            or service_request.assigned_officer == user
        )

        if not is_related:
            return Response(
                {
                    "detail": (
                        "You are not allowed to access these comments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            comments = service_request.comments.all()

            serializer = CommentSerializer(
                comments,
                many=True,
            )

            return Response(serializer.data)

        serializer = CommentSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                request=service_request,
                author=user,
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="attachments",
        parser_classes=[MultiPartParser],
    )
    def attachments(self, request, pk=None):
        service_request = self.get_object()
        user = request.user

        is_related = (
            user.role == "admin"
            or service_request.citizen == user
            or service_request.assigned_officer == user
        )

        if not is_related:
            return Response(
                {
                    "detail": (
                        "You are not allowed to access "
                        "these attachments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            attachments = service_request.attachments.all()

            serializer = AttachmentSerializer(
                attachments,
                many=True,
            )

            return Response(serializer.data)

        serializer = AttachmentSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                request=service_request,
                uploaded_by=user,
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
