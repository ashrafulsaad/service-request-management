import django_filters

from .models import ServiceRequest


class ServiceRequestFilter(django_filters.FilterSet):
    created_at_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_at_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = ServiceRequest
        fields = [
            "status",
            "priority",
            "category",
            "assigned_officer",
        ]
