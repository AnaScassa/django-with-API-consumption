from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")
router.register(r"user-profile", UserProfileViewSet, basename="user-profile")

urlpatterns = router.urls

