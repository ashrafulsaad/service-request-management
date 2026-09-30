from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ServiceRequestViewSet,
    CommentViewSet,
    AttachmentViewSet,
    UserViewSet,
    AdminStatsView,
)


router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
)

router.register(
    "requests",
    ServiceRequestViewSet,
    basename="service-request",
)

router.register(
    "comments",
    CommentViewSet,
)

router.register(
    "attachments",
    AttachmentViewSet,
)

router.register(
    "users",
    UserViewSet,
    basename="user",
)


urlpatterns = router.urls + [
    path(
        "admin/stats/",
        AdminStatsView.as_view(),
        name="admin-stats",
    ),
]
