from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ServiceRequestViewSet,
    CommentViewSet,
    AttachmentViewSet,
)

router = DefaultRouter()

router.register("categories", CategoryViewSet)
router.register("requests", ServiceRequestViewSet,basename= "service-request",)
router.register("comments", CommentViewSet)
router.register("attachments", AttachmentViewSet)

urlpatterns = router.urls
